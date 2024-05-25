from rest_framework import serializers
from django.contrib.auth.models import User

from core.models import Conversation, Message

# user serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined']

# chat serializer
class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'name', 'user', 'agent', 'created_at']
        
# message serializer
class MessageSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'image', 'audio', 'message', 'from_agent', 'conversation','created_at']