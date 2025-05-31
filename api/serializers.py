from rest_framework import serializers
from .models import ChatMessage, Patient, MedicalRecord

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'nfc_id', 'name', 'created_at']

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id', 'patient', 'condition', 'description', 'created_at', 'documents']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'user_input', 'ai_response', 'created_at', 'patient']
        read_only_fields = ['ai_response', 'created_at']