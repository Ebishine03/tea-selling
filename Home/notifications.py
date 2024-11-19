# views.py
from django.http import JsonResponse
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def mark_notification_as_read(request, notification_id):
    if request.user.is_authenticated:
        Notification.objects.filter(id=notification_id, user=request.user).update(is_read=True)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=403)

def send_notification(user_id, message):
    channel_layer = get_channel_layer()
    notification = Notification.objects.create(user_id=user_id, message=message)
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "new_notification",
            "notification": {
                "id": notification.id,
                "message": notification.message,
                "is_read": notification.is_read,
            },
        },
    )
