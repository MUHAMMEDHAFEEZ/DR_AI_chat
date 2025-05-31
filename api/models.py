from django.db import models

# Create your models here.

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other')
]

BLOOD_TYPE_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-')
]

SEVERITY_CHOICES = [
    ('LOW', 'Low'),
    ('MODERATE', 'Moderate'),
    ('HIGH', 'High'),
    ('CRITICAL', 'Critical')
]

MESSAGE_TYPES = [
    ('QUERY', 'Query'),
    ('DIAGNOSIS', 'Diagnosis'),
    ('FOLLOW_UP', 'Follow Up'),
    ('EMERGENCY', 'Emergency')
]

class Patient(models.Model):
    nfc_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='O')
    blood_type = models.CharField(max_length=5, choices=BLOOD_TYPE_CHOICES, default='O+')
    emergency_contact = models.CharField(max_length=255, null=True, blank=True)
    allergies = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (NFC: {self.nfc_id})"

    def get_age(self):
        from datetime import date
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    condition = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    documents = models.FileField(upload_to='medical_records/', null=True, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MODERATE')
    doctor_notes = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.patient.name}'s record - {self.condition}"

    class Meta:
        ordering = ['-created_at']

class ChatMessage(models.Model):
    user_input = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='chat_messages', null=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='QUERY')
    confidence_score = models.FloatField(default=0.0)
    requires_follow_up = models.BooleanField(default=False)

    def __str__(self):
        return f"Chat at {self.created_at}"

    class Meta:
        ordering = ['-created_at']
