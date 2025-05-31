# DR AI Chat - Medical Records System with NFC Integration

## Overview
This system allows medical staff to access and manage patient records through NFC scanning, providing two main functionalities:
1. Access to patient medical records
2. AI-powered medical consultation system

### Key Features
- 🏥 Instant patient identification through NFC
- 📱 Mobile-friendly interface
- 🤖 AI-powered medical consultations
- 📄 Digital medical records management
- 🔒 Secure data handling
- 📊 Medical history tracking
- 🔍 Smart search and filtering
- 📱 Cross-platform support

## System Architecture

### Models
- **Patient**: Stores patient information and NFC identifiers
  - `nfc_id`: Unique identifier from NFC card
  - `name`: Patient's full name
  - `created_at`: Registration timestamp
  
- **MedicalRecord**: Contains patient medical history and documents
  - `patient`: Foreign key to Patient
  - `condition`: Medical condition name
  - `description`: Detailed description
  - `created_at`: Record creation date
  - `documents`: Attached medical files

- **ChatMessage**: Stores AI consultation history with context
  - `user_input`: Patient/Doctor query
  - `ai_response`: AI-generated response
  - `created_at`: Message timestamp
  - `patient`: Link to patient record

### API Endpoints

#### 1. NFC Scanning
```http
POST /api/nfc-scan/
```
Simulates NFC tag scanning to identify patients.

Parameters:
- `nfc_id` (string, required): The NFC tag's unique identifier

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

Error Responses:
- `400 Bad Request`: Missing or invalid NFC ID
- `500 Internal Server Error`: Server processing error

#### 2. Patient Options
```http
GET /api/patient/{patient_id}/options/
```
Returns available actions for a patient.

URL Parameters:
- `patient_id` (integer, required): The patient's unique identifier

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

Error Responses:
- `404 Not Found`: Patient not found
- `403 Forbidden`: Unauthorized access

#### 3. Medical Records
```http
GET /api/patient/{patient_id}/records/
POST /api/patient/{patient_id}/records/
```

##### View Records
Parameters:
- `condition` (string, optional): Filter records by condition
- `start_date` (date, optional): Filter records from date
- `end_date` (date, optional): Filter records to date

Example:
```powershell
# Get all records
Invoke-WebRequest -Uri 'http://localhost:8000/api/patient/1/records/' -Method Get

# Filter by condition
Invoke-WebRequest -Uri 'http://localhost:8000/api/patient/1/records/?condition=diabetes' -Method Get

# Filter by date range
Invoke-WebRequest -Uri 'http://localhost:8000/api/patient/1/records/?start_date=2024-01-01&end_date=2024-12-31' -Method Get
```

##### Add Record
Required Fields:
- `condition` (string): Medical condition name
- `description` (string): Detailed description
- `documents` (file, optional): Medical documents

Example:
```powershell
$headers = @{'Content-Type'='application/json'}
$body = @{
    'condition'='Diabetes Type 2'
    'description'='Patient diagnosed with Type 2 Diabetes in 2024. Regular insulin treatment.'
    'documents'=@{
        'name'='blood_test.pdf'
        'content'='base64_encoded_content'
    }
} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/patient/1/records/' -Method Post -Headers $headers -Body $body
```

#### 4. AI Chat System
```http
POST /api/chat/?patient_id={patient_id}
GET /api/chat/?patient_id={patient_id}
```

Features:
- Context-aware responses based on medical history
- Medical terminology understanding
- Symptom analysis
- Treatment suggestions (with disclaimer)

Example Chat Flow:
```powershell
# Starting a chat session
$headers = @{'Content-Type'='application/json'}
$body = @{
    'user_input'='I have been experiencing frequent headaches and dizziness'
} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/chat/?patient_id=1' -Method Post -Headers $headers -Body $body

# Following up
$body = @{
    'user_input'='Is this related to my diabetes?'
} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/chat/?patient_id=1' -Method Post -Headers $headers -Body $body
```

## Features in Detail

### 1. NFC Integration
- Scans patient NFC tags
- Automatically creates new patient records if not found
- Redirects to patient options interface
- Supports multiple NFC formats
- Quick and secure identification

### 2. Medical Records Management
- Store multiple medical conditions per patient
- Attach medical documents (PDF, images, etc.)
- Filter records by condition
- Chronological record keeping
- Document versioning
- Search functionality
- Export capabilities (PDF, CSV)
- Bulk import support

### 3. AI-Powered Chat System
- Context-aware medical consultations
- Integrates patient history into responses
- Uses MedLLaMA2 model for medical expertise
- Stores chat history for future reference
- Natural language processing
- Multilingual support
- Medical terminology understanding
- Symptom analysis
- Treatment suggestions
- Emergency detection
- Follow-up reminders

## Technical Implementation

### Database Schema

```python
class Patient(models.Model):
    nfc_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    # Additional fields
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_type = models.CharField(max_length=5, choices=BLOOD_TYPE_CHOICES)
    emergency_contact = models.CharField(max_length=255, null=True)
    allergies = models.TextField(blank=True)
    
class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    condition = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    documents = models.FileField(upload_to='medical_records/')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    doctor_notes = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True)

class ChatMessage(models.Model):
    user_input = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, null=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    confidence_score = models.FloatField(default=0.0)
    requires_follow_up = models.BooleanField(default=False)
```

### AI Integration
The system uses Langchain with Ollama to provide medical consultations:
- Model: medllama2
- Context: Includes patient medical history
- Response format: Natural language medical advice
- Confidence scoring
- Emergency detection
- Follow-up flagging

Example prompt structure:
```
Patient Profile:
- Age: [age]
- Gender: [gender]
- Blood Type: [blood_type]
- Allergies: [allergies]

Medical History:
- Condition 1: [Description]
  Last updated: [date]
  Severity: [severity]
  Treatment: [treatment_plan]
- Condition 2: [Description]
  ...

Current Medications:
- [medication_list]

Current query: [User Question]
```

## Setup Instructions

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv chatbot

# Activate environment
# Windows
.\chatbot\Scripts\Activate.ps1
# Linux/Mac
source chatbot/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Requirements include:
- Django==5.2.1
- djangorestframework==3.14.0
- langchain==0.1.0
- langchain-ollama==0.1.0
- Pillow==10.0.0
- python-dotenv==1.0.0

### 3. Database Setup
```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### 4. Start Services
```bash
# Start Ollama service (required for AI)
ollama run medllama2

# Start Django server
python manage.py runserver
```

## Security Considerations
- All endpoints require proper authentication
- Medical data is encrypted at rest
- NFC IDs are securely stored
- Access control based on medical staff roles
- HIPAA compliance measures
- Regular security audits
- Data backup procedures
- Audit logging
- Rate limiting
- Input validation
- XSS protection
- CSRF protection

## Development Guidelines

### Code Style
- Follow PEP 8
- Use meaningful variable names
- Document all functions
- Write unit tests
- Use type hints
- Handle exceptions properly

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push changes
git push origin feature/new-feature
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test api.tests.TestPatientAPI
```

Example test data creation:
```powershell
# Create test patient
$headers = @{'Content-Type'='application/json'}
$body = @{
    'nfc_id'='TEST123'
    'name'='John Doe'
    'date_of_birth'='1990-01-01'
    'gender'='M'
    'blood_type'='A+'
} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/nfc-scan/' -Method Post -Headers $headers -Body $body

# Add medical record with full details
$body = @{
    'condition'='Type 2 Diabetes'
    'description'='Initial diagnosis with high blood sugar levels'
    'severity'='Moderate'
    'doctor_notes'='Patient responds well to medication'
    'treatment_plan'='Daily insulin injections and blood sugar monitoring'
    'follow_up_date'='2024-06-30'
} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/patient/1/records/' -Method Post -Headers $headers -Body $body

# Test chat with specific symptoms
$body = @{
    'user_input'='I have been experiencing blurred vision and increased thirst'
} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/chat/?patient_id=1' -Method Post -Headers $headers -Body $body
```

## Troubleshooting

### Common Issues
1. NFC Scanning Issues
   - Check NFC reader permissions
   - Verify NFC tag format
   - Ensure proper tag placement

2. AI Service Issues
   - Verify Ollama service is running
   - Check model availability
   - Monitor memory usage

3. Database Issues
   - Check connections
   - Verify migrations
   - Monitor disk space

### Logging
```python
# Enable debug logging
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Write tests
5. Submit pull request

## License
MIT License

## Support
- GitHub Issues
- Documentation Wiki
- Email Support
- Community Forum

## Changelog
- v1.0.0: Initial release
- v1.1.0: Added document support
- v1.2.0: Enhanced AI capabilities
- v1.3.0: Added security features
