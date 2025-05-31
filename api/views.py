from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_ratelimit.decorators import ratelimit
from .serializers import ChatMessageSerializer, PatientSerializer, MedicalRecordSerializer
from .models import ChatMessage, Patient, MedicalRecord
from .permissions import IsMedicalStaff, IsPatientOwner
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger('django')

class NFCScanView(APIView):
    permission_classes = [IsAuthenticated, IsMedicalStaff]
    
    @method_decorator(ratelimit(key='user', rate='10/m', method=['POST']))
    def post(self, request):
        try:
            nfc_id = request.data.get('nfc_id')
            if not nfc_id:
                return Response(
                    {'error': 'NFC ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            patient, created = Patient.objects.get_or_create(
                nfc_id=nfc_id,
                defaults={'name': f'Patient-{nfc_id[:8]}'}
            )
            
            # Log access
            logger.info(f"NFC scan by {request.user} for patient {patient.id}")
            
            return Response({
                'patient': PatientSerializer(patient).data,
                'redirect_url': f'/api/patient/{patient.id}/options/'
            })
        except Exception as e:
            logger.error(f"NFC scan error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PatientOptionsView(APIView):
    permission_classes = [IsAuthenticated, IsMedicalStaff]
    
    @method_decorator(cache_page(60))
    @method_decorator(vary_on_cookie)
    def get(self, request, patient_id):
        try:
            patient = get_object_or_404(Patient, id=patient_id)
            return Response({
                'patient': PatientSerializer(patient).data,
                'options': [
                    {
                        'id': 'view_records',
                        'title': 'View Medical Records',
                        'url': f'/api/patient/{patient.id}/records/'
                    },
                    {
                        'id': 'new_diagnosis',
                        'title': 'Request New Diagnosis',
                        'url': f'/api/chat/?patient_id={patient.id}'
                    }
                ]
            })
        except Exception as e:
            logger.error(f"Error fetching patient options: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MedicalRecordView(APIView):
    permission_classes = [IsAuthenticated, IsMedicalStaff]
    
    @method_decorator(cache_page(30))
    @method_decorator(vary_on_cookie)
    def get(self, request, patient_id):
        try:
            patient = get_object_or_404(Patient, id=patient_id)
            condition = request.query_params.get('condition')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            records = patient.medical_records.all()
            
            if condition:
                records = records.filter(condition__icontains=condition)
            if start_date:
                records = records.filter(created_at__gte=start_date)
            if end_date:
                records = records.filter(created_at__lte=end_date)
                
            return Response(MedicalRecordSerializer(records, many=True).data)
        except Exception as e:
            logger.error(f"Error fetching medical records: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @method_decorator(ratelimit(key='user', rate='30/m', method=['POST']))
    def post(self, request, patient_id):
        try:
            patient = get_object_or_404(Patient, id=patient_id)
            data = {**request.data, 'patient': patient.id}
            
            # Handle file upload
            if 'documents' in request.FILES:
                document = request.FILES['documents']
                path = default_storage.save(
                    f'medical_records/{patient.id}/{document.name}',
                    document
                )
                data['documents'] = path
            
            serializer = MedicalRecordSerializer(data=data)
            if serializer.is_valid():
                record = serializer.save()
                logger.info(f"Medical record created for patient {patient.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating medical record: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ChatView(APIView):
    permission_classes = [IsAuthenticated, IsMedicalStaff]
    
    @method_decorator(ratelimit(key='user', rate='60/m', method=['POST']))
    def post(self, request):
        try:
            serializer = ChatMessageSerializer(data=request.data)
            if serializer.is_valid():
                # Initialize the Llama model
                llm = OllamaLLM(model="medllama2")
                
                # Get user input and patient context
                user_input = serializer.validated_data['user_input']
                patient_id = request.query_params.get('patient_id')
                
                # Get patient context if available
                medical_context = ""
                if patient_id:
                    patient = get_object_or_404(Patient, id=patient_id)
                    records = patient.medical_records.all()
                    if records.exists():
                        medical_context = "Patient Profile:\n"
                        medical_context += f"- Age: {patient.get_age()}\n"
                        medical_context += f"- Gender: {patient.get_gender_display()}\n"
                        medical_context += f"- Blood Type: {patient.blood_type}\n"
                        medical_context += f"- Allergies: {patient.allergies}\n\n"
                        medical_context += "Medical History:\n"
                        for record in records:
                            medical_context += f"- {record.condition}: {record.description}\n"
                            medical_context += f"  Last updated: {record.updated_at}\n"
                            medical_context += f"  Severity: {record.get_severity_display()}\n"
                            medical_context += f"  Treatment: {record.treatment_plan}\n"
                
                # Prepare prompt with context
                prompt = f"{medical_context}\nCurrent query: {user_input}"
                
                # Get response from the model
                ai_response = llm.invoke(prompt)
                
                # Analyze response for emergency keywords
                emergency_keywords = ['emergency', 'immediate attention', 'critical', 'urgent']
                requires_follow_up = any(keyword in ai_response.lower() for keyword in emergency_keywords)
                
                # Save both the input and response
                chat_message = serializer.save(
                    ai_response=ai_response,
                    patient_id=patient_id if patient_id else None,
                    requires_follow_up=requires_follow_up,
                    message_type='EMERGENCY' if requires_follow_up else 'QUERY'
                )
                
                if requires_follow_up:
                    logger.warning(f"Emergency response detected for patient {patient_id}")
                
                return Response(ChatMessageSerializer(chat_message).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @method_decorator(cache_page(60))
    @method_decorator(vary_on_cookie)
    def get(self, request):
        try:
            patient_id = request.query_params.get('patient_id')
            messages = ChatMessage.objects.all()
            
            if patient_id:
                messages = messages.filter(patient_id=patient_id)
                
            messages = messages.order_by('-created_at')
            serializer = ChatMessageSerializer(messages, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching chat messages: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
