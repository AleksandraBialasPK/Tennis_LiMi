import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'events'
        await self.channel_layer.group_add('events', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('events', self.channel_name)

    async def receive(self, text_data):
        pass  # Not expecting any messages from clients

    async def send_event_update(self, event):
        await self.send(text_data=json.dumps(event))
