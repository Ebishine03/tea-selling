from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            # Add user to group based on user ID
            await self.channel_layer.group_add(
                f"user_{self.user.id}",  # Group name
                self.channel_name
            )
            await self.accept()

            # Send unread notifications to the user on connect
            unread_notifications = await self.get_unread_notifications()
            for notification in unread_notifications:
                await self.send(text_data=json.dumps({
                    "id": notification.id,
                    "message": notification.message,
                    "is_read": notification.is_read,
                }))
        else:
            await self.close()

    @sync_to_async
    def get_unread_notifications(self):
        # Fetch unread notifications from the database for the user
        return Notification.objects.filter(user=self.user, is_read=False)

    async def disconnect(self, close_code):
        # Remove user from the group on disconnect
        await self.channel_layer.group_discard(
            f"user_{self.user.id}",
            self.channel_name
        )

    async def new_notification(self, event):
        # Receive a notification from the channel layer and send it to the WebSocket
        await self.send(text_data=json.dumps(event["notification"]))
