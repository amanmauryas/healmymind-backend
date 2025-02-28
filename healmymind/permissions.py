from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return obj.user == request.user

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_admin

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Read-only permissions are allowed for any request.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_admin

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    Read-only permissions are allowed for any request.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow verified users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'is_verified', False)

class IsTestTaker(permissions.BasePermission):
    """
    Custom permission to only allow users who started a test to submit answers.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsChatParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a chat conversation to access it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsCommentAuthorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow comment authors or admins to modify comments.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_admin

class IsResourceManager(permissions.BasePermission):
    """
    Custom permission to only allow resource managers to modify support resources.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.is_admin or getattr(request.user, 'is_resource_manager', False))

class IsAnalyticsViewer(permissions.BasePermission):
    """
    Custom permission to only allow users with analytics viewing permissions.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.is_admin or getattr(request.user, 'can_view_analytics', False))
