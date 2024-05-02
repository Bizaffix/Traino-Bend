from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to add team members.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, or OPTIONS requests (read-only)
        if request.method in permissions.SAFE_METHODS:
            return True
        # This is custom permission on role bases
        return request.user and request.user.is_authenticated and request.user.role == 'Admin'
