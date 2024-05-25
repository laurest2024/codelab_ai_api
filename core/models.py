from datetime import datetime
import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# chats model
class Conversation(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    name = models.CharField(max_length=150, default="Asking question")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent = models.CharField(max_length=255, default='CHATGPT')
    created_at = models.DateTimeField(default=datetime.now())
    
    def __str__(self):
        return self.name
    
# messages model
class Message(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    image = models.ImageField(upload_to='message/images/', blank=True, null=True)
    audio = models.ImageField(upload_to='message/audios/', blank=True, null=True)
    message = models.TextField()
    from_agent= models.BooleanField(default=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now())
    
    def __str__(self):
        return self.message