from rest_framework import permissions


class IsClient(permissions.BasePermission):
    """Allows access only to authenticated users with Client role."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'client' or request.user.is_staff or request.user.is_superuser)
        )


class IsFreelancer(permissions.BasePermission):
    """Allows access only to authenticated users with Freelancer role."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'freelancer' or request.user.is_staff or request.user.is_superuser)
        )


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """Allows read access to everyone, write access only to Admin."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and (request.user.is_staff or request.user.role == 'admin'))


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allows modify access only to the owner of the object."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, 'user', None) or getattr(obj, 'created_by', None) or getattr(obj, 'client', None) or getattr(obj, 'freelancer', None)
        if owner is not None:
            if hasattr(owner, 'user'):
                return owner.user == request.user or request.user.is_staff
            return owner == request.user or request.user.is_staff
        return False
