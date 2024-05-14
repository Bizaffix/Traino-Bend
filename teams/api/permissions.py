from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from company.models import AdminUser
class IsActiveAdminPermission(permissions.BasePermission):
    """
    Custom permission to allow adding members only if the requesting admin's account is active.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.role == "Admin":
            try:
                admin_user = user.team_admin.get(admin=user)
                if not admin_user.is_active:
                    raise PermissionDenied("Your account is restricted. You cannot add members.")
            except AdminUser.DoesNotExist:
                raise PermissionDenied("AdminUser does not exist for the current user.")
        return True

from teams.models import CompaniesTeam

class IsActiveAdminUsersPermission(permissions.BasePermission):
    message = "You are not authorized to perform this action."

    def has_permission(self, request, view):
        # Check if the requesting user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if the requesting user is an admin
        try:
            admin = AdminUser.objects.get(admin=request.user, is_active=True)
        except AdminUser.DoesNotExist:
            return False
        
        # Check if the admin is associated with a company
        if not admin.company:
            return False
        
        return True

    def has_object_permission(self, request, view, obj):
        # Check if the requesting user is associated with the same company as the admin
        try:
            admin = AdminUser.objects.get(admin=request.user, is_active=True)
        except AdminUser.DoesNotExist:
            return False

        # Check if the user to be deleted belongs to the same company as the admin
        if isinstance(obj, CompaniesTeam):
            return obj.company == admin.company

        return False

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to add team members.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, or OPTIONS requests (read-only)
        if (request.user and request.user.is_authenticated and request.user.role == 'Super Admin'):#or (request.user and request.user.is_authenticated and request.user.role == 'User')
            if request.method in permissions.SAFE_METHODS:
                return True
        return request.user and request.user.is_authenticated and request.user.role == 'Admin' 

    def has_object_permission(self, request, view, obj):
        # Check if the requesting user is associated with the same company as the admin
        try:
            admin = AdminUser.objects.get(admin=request.user, is_active=True)
        except AdminUser.DoesNotExist:
            return False

        # Check if the user to be deleted belongs to the same company as the admin
        if isinstance(obj, CompaniesTeam):
            return obj.company == admin.company

        return request.user and request.user.is_authenticated and request.user.role == 'Admin' and obj.company == admin.company
