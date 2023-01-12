from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from djangorestframework_camel_case.util import camelize, underscoreize

from app.chat.models import Chat, Message


class ChatConsumer(AsyncJsonWebsocketConsumer):
    user = None

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                str(self.user.pk),
                self.channel_name,
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            str(self.user.pk),
            self.channel_name,
        )

    async def receive_json(self, content, **kwargs):
        content = underscoreize(content)
        message = await self.create_message(content)
        chat = await self.get_chat(message.chat)
        for user in chat.user_set.all():
            await self.channel_layer.group_send(
                str(user.pk),
                {
                    "type": "send_json",
                    "kind": "message",
                    "data": content,
                },
            )

    async def send_json(self, content, close=False):
        del content["type"]
        await super().send_json(dict(camelize(content)), close)

    @database_sync_to_async
    def get_chat(self, chat_id):
        try:
            chat = self.user.chat_set.prefetch_related("user_set").get(pk=chat_id)
        except Chat.DoesNotExist:
            chat = None
        return chat

    @database_sync_to_async
    def create_message(self, data):
        message = Message.objects.create(
            chat_id=data["chat_id"],
            user=self.user,
            text=data["text"],
        )
        # 상대에게 푸시알림 전송(by celery)
        return message
