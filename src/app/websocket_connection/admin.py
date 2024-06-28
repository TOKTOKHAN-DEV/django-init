from django.contrib import admin

from app.websocket_connection.models import WebsocketConnection


@admin.register(WebsocketConnection)
class WebsocketConnectionAdmin(admin.ModelAdmin):
    pass
