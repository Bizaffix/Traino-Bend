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
        """
        Custom permission to only allow admin users to update or view items that are related to their own company.
        """
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        
        # # Write permissions are only allowed if the user is an admin and the object's company is the same as the user's
        return request.user.role == 'Admin' and obj.company == request.user.adminuser.company