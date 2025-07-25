from channels.generic.websocket import AsyncWebsocketConsumer
import json


class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"
        print(self.group_name)

        print(f"[WebSocket CONNECTED] User ID: {self.user_id}")

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print(f"[WebSocket DISCONNECTED] User ID: {self.user_id}")
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def order_status_update(self, event):
        print(f"[WebSocket SEND] Sending event to user {self.user_id}: {event['content']}")
        await self.send(text_data=json.dumps(event['content']))