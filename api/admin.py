from django.contrib import admin
from .models import ChatMessage, Patient, MedicalRecord

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'nfc_id', 'created_at')
    search_fields = ('name', 'nfc_id')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'condition', 'created_at')
    list_filter = ('condition', 'created_at')
    search_fields = ('patient__name', 'condition', 'description')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user_input', 'patient')
    list_filter = ('created_at',)
    search_fields = ('user_input', 'ai_response', 'patient__name')
