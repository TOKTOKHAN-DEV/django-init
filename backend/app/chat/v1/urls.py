from django.urls import path

from app.chat.v1.views import ChatListView, MessageListView

urlpatterns = [
    path("chat/", ChatListView.as_view()),
    path("chat/<int:pk>/message/", MessageListView.as_view()),
]
