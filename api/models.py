from django.db import models

# Create your models here.

class Patient(models.Model):
    nfc_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (NFC: {self.nfc_id})"

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    condition = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    documents = models.FileField(upload_to='medical_records/', null=True, blank=True)

    def __str__(self):
        return f"{self.patient.name}'s record - {self.condition}"

class ChatMessage(models.Model):
    user_input = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='chat_messages', null=True)

    def __str__(self):
        return f"Chat at {self.created_at}"
