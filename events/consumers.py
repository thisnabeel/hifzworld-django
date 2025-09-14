import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class WebRTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection."""
        self.event_code = self.scope['url_route']['kwargs']['event_code']
        self.room_group_name = f"webrtc_{self.event_code}"

        logger.info(f"🔗 WebSocket connected: Event Code {self.event_code}")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection."""
        logger.info(f"❌ WebSocket disconnected: {self.event_code} (Code {close_code})")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handles incoming messages and broadcasts to the group."""
        try:
            data = json.loads(text_data)
            if "type" not in data:
                logger.warning(f"⚠️ Invalid WebRTC message received: {data}")
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_signal",
                    "message": data
                }
            )
            logger.debug(f"📩 WebRTC message relayed: {data}")

        except json.JSONDecodeError:
            logger.error("❌ Failed to parse WebSocket message. Ignoring invalid JSON.")

    async def send_signal(self, event):
        """Sends a WebRTC signaling message to the client."""
        try:
            await self.send(text_data=json.dumps(event["message"]))
        except Exception as e:
            logger.error(f"❌ Error sending WebSocket message: {e}")

