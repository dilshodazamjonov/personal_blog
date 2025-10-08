from rest_framework import permissions

class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read allowed for anyone (override later if needed)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write allowed only for author or admin
        return obj.author == request.user or request.user.is_staff