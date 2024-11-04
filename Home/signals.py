from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from Products .models import Order  # Adjust the import according to your project structure

@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, **kwargs):
    if instance.status in ['shipped', 'delivered', 'canceled']:
        message = f"Your order #{instance.id} status has changed to {instance.status.capitalize()}."
        Notification.objects.create(user=instance.customer, message=message)