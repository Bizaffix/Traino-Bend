from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow users who added the CustomUser or super admins to modify the CustomUser data.
    """
    def has_permission(self, request, view):
        # Log for debugging
        logger.debug(f"User: {request.user}, Authenticated: {request.user.is_authenticated}, Method: {request.method}")

        # Check if it's a safe method; if so, allow read-only access
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Ensure user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Check role for non-safe methods
        is_authorized_role = request.user.role in ['Super Admin', 'Admin']
        logger.debug(f"Is authorized role: {is_authorized_role}")
        return is_authorized_role

    def has_object_permission(self, request, view, obj):
        # Log for debugging
        logger.debug(f"Object added by: {obj.added_by}, User requesting: {request.user}")

        # Read permissions are allowed for any request,
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require conditions
        return request.user or request.user.role == 'Super Admin' or request.user or request.user.role == 'Admin'
        # can_edit = obj.added_by == request.user or request.user.role == 'Super Admin'
        # logger.debug(f"Can edit: {can_edit}")
        # return can_edit
