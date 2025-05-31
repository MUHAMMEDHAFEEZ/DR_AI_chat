from django.urls import path
from .views import ChatView, NFCScanView, PatientOptionsView, MedicalRecordView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('nfc-scan/', NFCScanView.as_view(), name='nfc_scan'),
    path('patient/<int:patient_id>/options/', PatientOptionsView.as_view(), name='patient_options'),
    path('patient/<int:patient_id>/records/', MedicalRecordView.as_view(), name='medical_records'),
]