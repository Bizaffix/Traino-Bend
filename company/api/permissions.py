from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to add team members.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, or OPTIONS requests (read-only)
        # if (request.user and request.user.is_authenticated and request.user.role == 'Super Admin'):#or (request.user and request.user.is_authenticated and request.user.role == 'User')
        #     if request.method in permissions.SAFE_METHODS:
        #         return True
        # This is custom permission on role bases
        return (request.user and request.user.is_authenticated and request.user.role == 'Super Admin') or (request.user and request.user.is_authenticated and request.user.role == 'Admin')

    # def has_object_permission(self, request, view, obj):
    #     """
    #     Custom permission to only allow admin users to update their own items.
    #     """
    #     # Allow admins to update their own items
    #     if request.user.role == 'Super Admin':
    #         # Check if the user updating the item is the same as the item's added_by user
            
    #         return obj.added_by == request.user
    #     # Deny access if the user is not an admin or if they are trying to update someone else's item
    #     return False
    
class IsAdminListOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to add team members.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, or OPTIONS requests (read-only)
        # if (request.user and request.user.is_authenticated and request.user.role == 'Super Admin'):#or (request.user and request.user.is_authenticated and request.user.role == 'User')
        #     if request.method in permissions.SAFE_METHODS:
        #         return True
        # This is custom permission on role bases
        return request.user and request.user.is_authenticated and request.user.role == 'Super Admin' or request.user and request.user.is_authenticated and request.user.role == 'Admin'