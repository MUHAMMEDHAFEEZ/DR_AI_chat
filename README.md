# DR AI Chat - Medical Records System with NFC Integration

## Overview
This system allows medical staff to access and manage patient records through NFC scanning, providing two main functionalities:
1. Access to patient medical records
2. AI-powered medical consultation system

## System Architecture

### Models
- **Patient**: Stores patient information and NFC identifiers
- **MedicalRecord**: Contains patient medical history and documents
- **ChatMessage**: Stores AI consultation history with context

### API Endpoints

#### 1. NFC Scanning
```http
POST /api/nfc-scan/
```
Simulates NFC tag scanning to identify patients.

Example:
```powershell
$headers = @{'Content-Type'='application/json'}
$body = @{'nfc_id'='PATIENT123'} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/nfc-scan/' -Method Post -Headers $headers -Body $body
```

Response:
```json
{
    "patient": {
        "id": 1,
        "nfc_id": "PATIENT123",
        "name": "Patient-PATIENT1",
        "created_at": "2025-05-31T00:19:53.634662Z"
    },
    "redirect_url": "/api/patient/1/options/"
}
```

#### 2. Patient Options
```http
GET /api/patient/{patient_id}/options/
```
Returns available actions for a patient.

Example:
```powershell
Invoke-WebRequest -Uri 'http://localhost:8000/api/patient/1/options/' -Method Get
```

Response:
```json
{
    "patient": {
        "id": 1,
        "nfc_id": "PATIENT123",
        "name": "Patient-PATIENT1"
    },
    "options": [
        {
            "id": "view_records",
            "title": "View Medical Records",
            "url": "/api/patient/1/records/"
        },
        {
            "id": "new_diagnosis",
            "title": "Request New Diagnosis",
            "url": "/api/chat/?patient_id=1"
        }
    ]
}
```

#### 3. Medical Records
```http
GET /api/patient/{patient_id}/records/
POST /api/patient/{patient_id}/records/
```

View Records Example:
```powershell
Invoke-WebRequest -Uri 'http://localhost:8000/api/patient/1/records/' -Method Get
```

Add Record Example:
```powershell
$headers = @{'Content-Type'='application/json'}
$body = @{
    'condition'='Diabetes Type 2'
    'description'='Patient diagnosed with Type 2 Diabetes in 2024. Regular insulin treatment.'
} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/patient/1/records/' -Method Post -Headers $headers -Body $body
```

Filter by Condition:
```http
GET /api/patient/{patient_id}/records/?condition=diabetes
```

#### 4. AI Chat System
```http
POST /api/chat/?patient_id={patient_id}
GET /api/chat/?patient_id={patient_id}
```

Chat Example:
```powershell
$headers = @{'Content-Type'='application/json'}
$body = @{
    'user_input'='What are my current symptoms indicating?'
} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/chat/?patient_id=1' -Method Post -Headers $headers -Body $body
```

## Features in Detail

### 1. NFC Integration
- Scans patient NFC tags
- Automatically creates new patient records if not found
- Redirects to patient options interface

### 2. Medical Records Management
- Store multiple medical conditions per patient
- Attach medical documents (PDF, images, etc.)
- Filter records by condition
- Chronological record keeping

### 3. AI-Powered Chat System
- Context-aware medical consultations
- Integrates patient history into responses
- Uses MedLLaMA2 model for medical expertise
- Stores chat history for future reference

## Technical Implementation

### Database Schema

```python
class Patient(models.Model):
    nfc_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    condition = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    documents = models.FileField(upload_to='medical_records/')

class ChatMessage(models.Model):
    user_input = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, null=True)
```

### AI Integration
The system uses Langchain with Ollama to provide medical consultations:
- Model: medllama2
- Context: Includes patient medical history
- Response format: Natural language medical advice

Example prompt structure:
```
Patient medical history:
- Condition 1: Description
- Condition 2: Description

Current query: [User Question]
```

## Setup Instructions

1. Install Dependencies:
```bash
pip install -r requirements.txt
```

2. Run Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Start the Server:
```bash
python manage.py runserver
```

## Security Considerations
- All endpoints require proper authentication (to be implemented)
- Medical data is sensitive and should be encrypted
- NFC IDs should be securely stored
- Access control based on medical staff roles

## Future Enhancements
1. Medical staff authentication system
2. Document encryption
3. Multi-language support
4. Emergency contact information
5. Appointment scheduling
6. Medication tracking
7. Lab results integration
8. Real-time notifications

## API Documentation
Full OpenAPI/Swagger documentation available at:
```
/api/docs/
```

## Testing
Run the test suite:
```bash
python manage.py test
```

Example test data creation:
```powershell
# Create test patient
$headers = @{'Content-Type'='application/json'}
$body = @{'nfc_id'='TEST123'} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/nfc-scan/' -Method Post -Headers $headers -Body $body

# Add medical record
$body = @{
    'condition'='Test Condition'
    'description'='Test Description'
} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/patient/1/records/' -Method Post -Headers $headers -Body $body

# Test chat
$body = @{'user_input'='Test question'} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/chat/?patient_id=1' -Method Post -Headers $headers -Body $body
```
