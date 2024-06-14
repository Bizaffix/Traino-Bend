from rest_framework import permissions
from company.models import AdminUser
from teams.models import CompaniesTeam
from departments.models import Departments , DepartmentsDocuments

class IsAdminUserAndSameCompany(permissions.BasePermission):
    """
    Custom permission to only allow admin users to view and manage data if it pertains to their own company.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'Admin'

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission to ensure admins can only manage items related to their own company.
        """
        return request.user.adminuser.company == obj.company


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to add team members.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, or OPTIONS requests (read-only)
        if request.method in permissions.SAFE_METHODS:
            return True
        # # This is custom permission on role bases
        return (request.user and request.user.is_authenticated and request.user.role == 'Admin') or (request.user and request.user.is_authenticated and request.user.role == 'Super Admin') 

    def has_object_permission(self, request, view, obj):
        """
        Custom permission to only allow admin users to update or view items that are related to their own company.
        """
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # # Write permissions are only allowed if the user is an admin and the object's company is the same as the user's
        if request.user.role == "Admin":
            # print(request.user)
            admin = AdminUser.objects.get(admin=request.user)
            # print(str(obj.company.id), str(admin.company.id))
            if str(obj.company.id) == str(admin.company.id):
                if admin.is_active==True: 
                    return True
            return False
        
        if request.user.role == "User":
            user = request.user
            # print(user)
            team_member = user.team_member.all()
            user_departments = Departments.objects.filter(users__in=team_member, is_active=True)
            # print(obj.company.id)
            # print(user_departments.company.id)
            if obj in user_departments:
                return True
            return False
        
from rest_framework.permissions import BasePermission

class IsAssociatedWithDepartment(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "User":
            member = CompaniesTeam.objects.filter(members=request.user, is_active=True).first()
            user_departments = Departments.objects.filter(users=member, is_active=True)
            if not user_departments.exists():
                return False
            quiz_id = request.data.get("quiz_id")
            quiz_id = request.data.get("quiz_id")
            document = DepartmentsDocuments.objects.filter(id=quiz_id, is_active=True).first()
            if not document:
                return False
            document_department = document.department

            if not user_departments.filter(id=document_department.id).exists():
                return False
        return True