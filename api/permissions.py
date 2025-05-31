from rest_framework import permissions

class IsMedicalStaff(permissions.BasePermission):
    """
    Custom permission to only allow medical staff members to access the view.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.groups.filter(name='Medical Staff').exists())

class IsPatientOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a patient record to view it.
    """
    def has_object_permission(self, request, view, obj):
        # Only allow if the user is assigned to the patient
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.groups.filter(name='Medical Staff').exists() or
                    obj.assigned_staff.filter(id=request.user.id).exists()))
