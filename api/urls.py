from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ChatView, NFCScanView, PatientOptionsView, MedicalRecordView
from .auth_views import RegisterView, LoginView, LogoutView

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('chat/', ChatView.as_view(), name='chat'),
    path('nfc-scan/', NFCScanView.as_view(), name='nfc_scan'),
    path('patient/<int:patient_id>/options/', PatientOptionsView.as_view(), name='patient_options'),
    path('patient/<int:patient_id>/records/', MedicalRecordView.as_view(), name='medical_records'),
]