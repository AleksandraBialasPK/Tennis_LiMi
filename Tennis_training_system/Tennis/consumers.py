import json
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from channels.db import database_sync_to_async
from Tennis.models import Game

class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'events'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        current_date = now().date()
        await self.send_event_update_for_date(current_date)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        date_str = data.get('date')
        if date_str:
            date = parse_date(date_str)
            if date:
                await self.send_event_update_for_date(date)

    async def send_event_update_for_date(self, date):
        events = await self.get_events_for_date(date)

        for event in events:
            event['start_date_and_time'] = event['start_date_and_time'].strftime('%Y-%m-%d %H:%M:%S')
            event['end_date_and_time'] = event['end_date_and_time'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"Converted event: {event}")

        current_date_info = {
            'current_date': date.strftime('%d'),
            'current_month': date.strftime('%B'),
            'current_year': date.strftime('%Y'),
            'prev_date': (date - timedelta(days=1)).strftime('%Y-%m-%d'),
            'next_date': (date + timedelta(days=1)).strftime('%Y-%m-%d'),
        }

        print(f"Events fetched for date {date.isoformat()}: {events}")
        print(f"Sending data: {current_date_info}")

        await self.send(text_data=json.dumps({
            'type': 'initial_event_load',
            'events': events,
            **current_date_info,
        }))

    @database_sync_to_async
    def get_events_for_date(self, date):
        events = Game.objects.filter(start_date_and_time__date=date).values(
            'name', 'category__name', 'start_date_and_time', 'end_date_and_time'
        )
        return list(events)
