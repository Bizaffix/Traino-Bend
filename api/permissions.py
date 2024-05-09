from rest_framework import permissions


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
        if (request.user and request.user.is_authenticated and request.user.role == 'Super Admin') or (request.user and request.user.is_authenticated and request.user.role == 'User'):
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
        if request.user.role == 'Admin' and obj.added_by == request.user:
            if request.method in permissions.SAFE_METHODS:
                return True
        
        # # Write permissions are only allowed if the user is an admin and the object's company is the same as the user's
        return request.user.role == 'Admin' and obj.added_by == request.user