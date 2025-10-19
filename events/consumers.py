import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)

class WebRTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection."""
        try:
            # Extract event_code from URL path
            self.event_code = self.scope['url_route']['kwargs']['event_code']
            self.room_group_name = f"webrtc_{self.event_code}"
            
            # Accept the connection first to avoid connection timeouts
            await self.accept()
            
            # Add to room group after accepting
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            
            logger.info(f"✅ WebSocket connected: Event {self.event_code}")
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {type(e).__name__}: {e}")
            try:
                await self.close()
            except:
                pass

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        try:
            logger.info(f"❌ WebSocket disconnected: {getattr(self, 'event_code', 'unknown')} (Code {close_code})")
            if hasattr(self, 'room_group_name') and hasattr(self, 'channel_name') and hasattr(self, 'channel_layer'):
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception as e:
            logger.error(f"❌ Error during disconnect: {type(e).__name__}: {e}")

    async def receive(self, text_data):
        """Handles incoming messages and broadcasts to the group."""
        try:
            data = json.loads(text_data)
            if "type" not in data:
                logger.warning("⚠️ Invalid WebRTC message received")
                return

            message_type = data.get("type", "unknown")
            logger.debug(f"📨 Received message type: {message_type}")
            
            # Handle check-room message - notify other users that someone joined
            if message_type == "check-room":
                try:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "send_signal",
                            "message": {"type": "user-joined"},
                            "sender_channel": self.channel_name
                        }
                    )
                    logger.info(f"📱 User joined room {getattr(self, 'event_code', 'unknown')}")
                except Exception as e:
                    logger.error(f"❌ Error sending user-joined signal: {e}")
                return

            # Handle all other WebRTC signaling messages
            try:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_signal",
                        "message": data,
                        "sender_channel": self.channel_name
                    }
                )
                logger.debug(f"📩 WebRTC message relayed: {message_type}")
            except Exception as e:
                logger.error(f"❌ Error sending group message: {e}")

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse WebSocket message: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error in receive: {e}")

    async def send_signal(self, event):
        """Sends a WebRTC signaling message to the client."""
        try:
            # Don't send the message back to the sender
            sender_channel = event.get("sender_channel")
            if sender_channel and sender_channel == self.channel_name:
                return
                
            message = event.get("message", {})
            if message and isinstance(message, dict):
                message_type = message.get("type", "unknown")
                await self.send(text_data=json.dumps(message))
                logger.debug(f"📤 WebRTC signal sent: {message_type}")
        except (ConnectionResetError, ConnectionAbortedError) as e:
            logger.warning(f"📤 Connection lost during send: {e}")
        except Exception as e:
            logger.error(f"❌ Error sending WebSocket message: {type(e).__name__}: {e}")
            # Don't log the full message to avoid memory issues


class MatchmakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection for matchmaking."""
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f"matchmaking_{self.user_id}"
        
        logger.info(f"🔗 Matchmaking WebSocket connected: User {self.user_id}")
        
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()
        
        # Update user's online status
        await self.update_user_online_status(True)

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection for matchmaking."""
        logger.info(f"❌ Matchmaking WebSocket disconnected: User {self.user_id}")
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        
        # Update user's online status
        await self.update_user_online_status(False)

    @database_sync_to_async
    def update_user_online_status(self, is_online):
        """Update user's online status."""
        try:
            User = get_user_model()
            user = User.objects.get(id=self.user_id)
            user.is_online = is_online
            user.last_seen = timezone.now()
            user.save()
        except Exception as e:
            logger.error(f"User {self.user_id} not found for online status update: {e}")

    async def receive(self, text_data):
        """Handles incoming matchmaking messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'heartbeat':
                await self.update_user_online_status(True)
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat_response',
                    'timestamp': timezone.now().isoformat()
                }))
            elif message_type == 'request_match':
                await self.handle_match_request(data)
            elif message_type == 'notification':
                # Forward notification to specific user
                await self.send_notification_to_user(data)
                
        except json.JSONDecodeError:
            logger.error("❌ Failed to parse matchmaking WebSocket message")

    async def handle_match_request(self, data):
        """Handle matchmaking request notifications."""
        target_user_id = data.get('target_user_id')
        if target_user_id:
            target_group = f"matchmaking_{target_user_id}"
            await self.channel_layer.group_send(
                target_group,
                {
                    'type': 'matchmaking_notification',
                    'message': data
                }
            )

    async def send_notification_to_user(self, data):
        """Send notification to the connected user."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': data
        }))

    async def matchmaking_notification(self, event):
        """Send matchmaking notification to client."""
        await self.send(text_data=json.dumps({
            'type': 'matchmaking_notification',
            'data': event['message']
        }))

    async def friend_status_update(self, event):
        """Send friend status update to client."""
        await self.send(text_data=json.dumps({
            'type': 'friend_status_update',
            'data': event['message']
        }))

    async def match_status_update(self, event):
        """Send match status update to client."""
        await self.send(text_data=json.dumps({
            'type': 'match_status_update',
            'data': event['message']
        }))

    async def room_notification(self, event):
        """Send room notification to client."""
        await self.send(text_data=json.dumps({
            'type': 'room_notification',
            'data': event['message']
        }))

