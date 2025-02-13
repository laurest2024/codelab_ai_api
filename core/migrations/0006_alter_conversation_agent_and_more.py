# Generated by Django 5.0.4 on 2024-05-23 12:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_messagemodel_chat_conversation_message_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='agent',
            field=models.CharField(blank=True, default='CHATGPT', max_length=255),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 23, 13, 36, 50, 643277)),
        ),
        migrations.AlterField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 23, 13, 36, 50, 644277)),
        ),
    ]
