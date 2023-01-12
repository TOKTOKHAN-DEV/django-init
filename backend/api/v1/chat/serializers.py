from rest_framework import serializers

from app.chat.models import Chat, Message


class ChatListSerializer(serializers.ModelSerializer):
    last_message = serializers.CharField(source="get_last_message")
    updated = serializers.DateTimeField()

    class Meta:
        model = Chat
        fields = ["id", "last_message", "updated"]


class MessageListSerializer(serializers.ModelSerializer):
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["is_mine", "text", "image", "created"]

    def get_is_mine(self, obj):
        return self.context["request"].user == obj.user
