# Generated by Django 5.0.2 on 2024-11-08 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='notification_type',
            new_name='message_type',
        ),
    ]
