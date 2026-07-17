import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SeatSyncConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.theater_id = self.scope['url_route']['kwargs']['theater_id']
        self.room_group_name = f'theater_{self.theater_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket (frontend client)
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        seat_id = data.get('seat_id')

        # Broadcast the seat action to everyone in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'seat_update',
                'action': action,
                'seat_id': seat_id
            }
        )

    # Receive message from room group (broadcast)
    async def seat_update(self, event):
        action = event['action']
        seat_id = event['seat_id']

        # Send message back to the individual WebSocket connection
        await self.send(text_data=json.dumps({
            'action': action,
            'seat_id': seat_id
        }))
