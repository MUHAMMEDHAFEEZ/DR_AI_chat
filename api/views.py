from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChatMessageSerializer, PatientSerializer, MedicalRecordSerializer
from .models import ChatMessage, Patient, MedicalRecord
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

class NFCScanView(APIView):
    def post(self, request):
        nfc_id = request.data.get('nfc_id')
        if not nfc_id:
            return Response(
                {'error': 'NFC ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find or create patient
        patient, created = Patient.objects.get_or_create(
            nfc_id=nfc_id,
            defaults={'name': f'Patient-{nfc_id[:8]}'}  # Temporary name
        )
        
        return Response({
            'patient': PatientSerializer(patient).data,
            'redirect_url': f'/api/patient/{patient.id}/options/'
        })

class PatientOptionsView(APIView):
    def get(self, request, patient_id):
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

class MedicalRecordView(APIView):
    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, id=patient_id)
        condition = request.query_params.get('condition')
        
        records = patient.medical_records.all()
        if condition:
            records = records.filter(condition__icontains=condition)
            
        return Response(MedicalRecordSerializer(records, many=True).data)
    
    def post(self, request, patient_id):
        patient = get_object_or_404(Patient, id=patient_id)
        data = {**request.data, 'patient': patient.id}
        serializer = MedicalRecordSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatView(APIView):
    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            # Initialize the Llama model
            llm = OllamaLLM(model="medllama2")
            
            # Get user input and patient context
            user_input = serializer.validated_data['user_input']
            patient_id = request.query_params.get('patient_id')
            
            try:
                # Get patient context if available
                medical_context = ""
                if patient_id:
                    patient = get_object_or_404(Patient, id=patient_id)
                    records = patient.medical_records.all()
                    if records.exists():
                        medical_context = "Patient medical history:\n"
                        for record in records:
                            medical_context += f"- {record.condition}: {record.description}\n"
                
                # Prepare prompt with context
                prompt = f"{medical_context}\nCurrent query: {user_input}"
                
                # Get response from the model
                ai_response = llm.invoke(prompt)
                
                # Save both the input and response
                chat_message = serializer.save(
                    ai_response=ai_response,
                    patient_id=patient_id if patient_id else None
                )
                
                return Response(ChatMessageSerializer(chat_message).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        patient_id = request.query_params.get('patient_id')
        messages = ChatMessage.objects.all()
        
        if patient_id:
            messages = messages.filter(patient_id=patient_id)
            
        messages = messages.order_by('-created_at')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
