from rest_framework import permissions
from company.models import AdminUser
from teams.models import CompaniesTeam
from departments.models import Departments
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
        return request.user and request.user.is_authenticated and request.user.role == 'Admin' 

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
            print(request.user)
            admin = AdminUser.objects.get(admin=request.user)
            print(str(obj.company.id), str(admin.company.id))
            if str(obj.company.id) == str(admin.company.id):
                if admin.is_active==True: 
                    return True
            return False
        
        if request.user.role == "User":
            user = request.user
            print(user)
            team_member = user.team_member.all()
            user_departments = Departments.objects.filter(users__in=team_member, is_active=True)
            print(obj.company.id)
            # print(user_departments.company.id)
            if obj in user_departments:
                return True
            return False