from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from .models import Notification
from Products .models import Order  ,Product
from django.db.models.signals import post_save
from django.dispatch import receiver
from  .notifications  import send_notification  # Use your notification utility
# Adjust the import according to your project structure


