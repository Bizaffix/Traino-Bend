from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to add team members.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, or OPTIONS requests (read-only)
        if (request.user and request.user.is_authenticated and request.user.role == 'Super Admin')or (request.user and request.user.is_authenticated and request.user.role == 'User'):#
            if request.method in permissions.SAFE_METHODS:
                return True
        return request.user and request.user.is_authenticated and request.user.role == 'Admin' 

    def has_object_permission(self, request, view, obj):
        """
        Custom permission to only allow admin users to update or view items that are related to their own company.
        """
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        
        # # Write permissions are only allowed if the user is an admin and the object's company is the same as the user's
        return request.user.role == 'Admin'
    
from company.models import AdminUser
from departments.models import Departments
class IsAdminUserOfCompany(permissions.BasePermission):
    """
    Custom permission to only allow admins of the same company to edit it.
    """
    def has_permission(self, request, view):
        department_id = request.data.get('department')
        if department_id:
            try:
                department = Departments.objects.get(id=department_id)
                # Check if the user is an admin of the same company as the department
                return AdminUser.objects.filter(admin=request.user, is_active=True, company=department.company).exists()
            except Departments.DoesNotExist:
                return False
        return False