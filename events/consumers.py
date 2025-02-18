import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WebRTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.event_code = self.scope['url_route']['kwargs']['event_code']
        self.room_group_name = f"webrtc_{self.event_code}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_signal",
                "message": data
            }
        )

    async def send_signal(self, event):
        await self.send(text_data=json.dumps(event["message"]))
