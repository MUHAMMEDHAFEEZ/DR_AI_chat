from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import Patient, MedicalRecord, ChatMessage

class Command(BaseCommand):
    help = 'Create default groups and permissions for medical staff'

    def handle(self, *args, **options):
        # Create Medical Staff group
        medical_staff, created = Group.objects.get_or_create(name='Medical Staff')
        if created:
            self.stdout.write(f'Created group: Medical Staff')
        
        # Get content types
        patient_ct = ContentType.objects.get_for_model(Patient)
        record_ct = ContentType.objects.get_for_model(MedicalRecord)
        chat_ct = ContentType.objects.get_for_model(ChatMessage)
        
        # Define permissions for each model
        permissions = {
            patient_ct: [
                ('view_patient', 'Can view patient'),
                ('add_patient', 'Can add patient'),
                ('change_patient', 'Can change patient'),
                ('delete_patient', 'Can delete patient'),
            ],
            record_ct: [
                ('view_medicalrecord', 'Can view medical record'),
                ('add_medicalrecord', 'Can add medical record'),
                ('change_medicalrecord', 'Can change medical record'),
                ('delete_medicalrecord', 'Can delete medical record'),
            ],
            chat_ct: [
                ('view_chatmessage', 'Can view chat message'),
                ('add_chatmessage', 'Can add chat message'),
                ('change_chatmessage', 'Can change chat message'),
                ('delete_chatmessage', 'Can delete chat message'),
            ]
        }
        
        # Create permissions and add to group
        for content_type, perms in permissions.items():
            for codename, name in perms:
                permission, created = Permission.objects.get_or_create(
                    codename=codename,
                    name=name,
                    content_type=content_type,
                )
                medical_staff.permissions.add(permission)
                if created:
                    self.stdout.write(f'Created permission: {name}')
                    
        self.stdout.write(self.style.SUCCESS('Successfully set up groups and permissions'))