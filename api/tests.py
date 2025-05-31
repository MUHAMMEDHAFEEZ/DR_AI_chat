from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Patient, MedicalRecord, ChatMessage
from datetime import date, timedelta

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testdoctor',
            'password': 'securepass123',
            'email': 'doctor@test.com',
            'first_name': 'Test',
            'last_name': 'Doctor'
        }

    def test_register(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('access' in response.data)
        self.assertTrue(User.objects.filter(username='testdoctor').exists())

    def test_login(self):
        # Create user first
        User.objects.create_user(username='testdoctor', password='securepass123')
        response = self.client.post(self.login_url, {
            'username': 'testdoctor',
            'password': 'securepass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

class PatientTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create medical staff user
        self.user = User.objects.create_user(username='doctor', password='pass123')
        self.medical_staff = Group.objects.create(name='Medical Staff')
        self.medical_staff.user_set.add(self.user)
        self.client.force_authenticate(user=self.user)

    def test_nfc_scan(self):
        url = reverse('nfc_scan')
        response = self.client.post(url, {'nfc_id': 'TEST123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Patient.objects.filter(nfc_id='TEST123').exists())

    def test_patient_options(self):
        patient = Patient.objects.create(
            nfc_id='TEST123',
            name='Test Patient',
            gender='M',
            blood_type='A+'
        )
        url = reverse('patient_options', kwargs={'patient_id': patient.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['options']), 2)

class MedicalRecordTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='doctor', password='pass123')
        self.medical_staff = Group.objects.create(name='Medical Staff')
        self.medical_staff.user_set.add(self.user)
        self.client.force_authenticate(user=self.user)
        self.patient = Patient.objects.create(
            nfc_id='TEST123',
            name='Test Patient',
            gender='M',
            blood_type='A+'
        )

    def test_create_record(self):
        url = reverse('medical_records', kwargs={'patient_id': self.patient.id})
        data = {
            'condition': 'Diabetes',
            'description': 'Type 2 Diabetes',
            'severity': 'MODERATE',
            'treatment_plan': 'Insulin therapy'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(MedicalRecord.objects.filter(condition='Diabetes').exists())

    def test_get_records(self):
        MedicalRecord.objects.create(
            patient=self.patient,
            condition='Diabetes',
            description='Type 2 Diabetes',
            severity='MODERATE'
        )
        url = reverse('medical_records', kwargs={'patient_id': self.patient.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_records(self):
        MedicalRecord.objects.create(
            patient=self.patient,
            condition='Diabetes',
            description='Type 2 Diabetes',
            severity='MODERATE'
        )
        MedicalRecord.objects.create(
            patient=self.patient,
            condition='Hypertension',
            description='High blood pressure',
            severity='LOW'
        )
        url = reverse('medical_records', kwargs={'patient_id': self.patient.id})
        response = self.client.get(f'{url}?condition=diabetes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ChatTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='doctor', password='pass123')
        self.medical_staff = Group.objects.create(name='Medical Staff')
        self.medical_staff.user_set.add(self.user)
        self.client.force_authenticate(user=self.user)
        self.patient = Patient.objects.create(
            nfc_id='TEST123',
            name='Test Patient',
            gender='M',
            blood_type='A+'
        )
        self.medical_record = MedicalRecord.objects.create(
            patient=self.patient,
            condition='Diabetes',
            description='Type 2 Diabetes',
            severity='MODERATE'
        )

    def test_chat_with_context(self):
        url = reverse('chat')
        data = {
            'user_input': 'What are my current symptoms indicating?'
        }
        response = self.client.post(f'{url}?patient_id={self.patient.id}', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(response.data['ai_response']) > 0)

    def test_chat_history(self):
        ChatMessage.objects.create(
            user_input='Test question',
            ai_response='Test response',
            patient=self.patient
        )
        url = reverse('chat')
        response = self.client.get(f'{url}?patient_id={self.patient.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
