from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'user_input', 'ai_response', 'created_at']
        read_only_fields = ['ai_response', 'created_at'] 