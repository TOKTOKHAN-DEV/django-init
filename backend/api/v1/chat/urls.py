from django.urls import path

from api.v1.chat.views import ChatListView, MessageListView

urlpatterns = [
    path("chat/", ChatListView.as_view()),
    path("chat/<int:pk>/message/", MessageListView.as_view()),
]
