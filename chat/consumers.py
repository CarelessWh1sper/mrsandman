import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import IntegrityError
from django.utils import timezone

from .models import Message, Room

MAX_LENGTH = 500


class ChatConsumer(AsyncWebsocketConsumer):
    """Anyone can watch a room live; only signed-in users can post."""

    async def connect(self):
        self.user = self.scope['user']
        pk = self.scope['url_route']['kwargs']['pk']

        self.room = await self.get_room(pk)
        if self.room is None:
            await self.close(code=4404)
            return

        self.group = f'chat_room_{self.room.pk}'
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not self.user.is_authenticated:
            return
        try:
            data = json.loads(text_data)
        except (TypeError, ValueError):
            return
        if not isinstance(data, dict):
            return

        text = str(data.get('message', '')).strip()[:MAX_LENGTH]
        if not text:
            return

        saved = await self.save_message(text)
        if saved is None: 
            await self.close(code=4404)
            return

        await self.channel_layer.group_send(self.group, {
            'type': 'chat.message',
            'id': saved.pk,
            'user_id': self.user.pk,
            'username': self.user.get_username(),
            'body': text,
            'time': saved.created.isoformat(),
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            key: event[key] for key in ('id', 'user_id', 'username', 'body', 'time')
        }))

    @database_sync_to_async
    def get_room(self, pk):
        return Room.objects.filter(pk=pk).first()

    @database_sync_to_async
    def save_message(self, text):
        try:
            message = Message.objects.create(room=self.room, user=self.user, body=text)
        except IntegrityError:
            return None
        self.room.participants.add(self.user)
        Room.objects.filter(pk=self.room.pk).update(updated=timezone.now())
        return message
