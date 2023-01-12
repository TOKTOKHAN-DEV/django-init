from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from api.v1.chat.paginations import MessagePagination
from api.v1.chat.serializers import ChatListSerializer, MessageListSerializer
from app.chat.models import Chat, Message


class ChatCreateView(CreateAPIView):

    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        str(user.pk),
        {
            'type': 'send_message',
            'chat_id': data['chat_id'],
            'user_id': message.user.pk,
            'text': message.text,
            'created': message.created,
        },
    )
    """

    pass


class ChatListView(ListAPIView):
    queryset = Chat.objects.prefetch_related("user_set").all()
    serializer_class = ChatListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(user_set=user)


class MessageListView(ListAPIView):
    queryset = Message.objects.select_related("user").all()
    serializer_class = MessageListSerializer
    pagination_class = MessagePagination

    # permission_classes = [IsChatOwner]

    def get_queryset(self):
        return self.queryset.filter(chat_id=self.kwargs["pk"])
