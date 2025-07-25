from rest_framework import permissions
from employees.models import Employee


class IsAdminOrHR(permissions.BasePermission):
    """
    Custom permission to only allow admin or HR users.
    """

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated and
                (request.user.is_superuser
                 or getattr(request.user, 'role', None) == 'HR'
                 or getattr(request.user, 'role', None) == 'Admin')
        )


class IsOwnerAdminOrHR(permissions.BasePermission):
    """
    Allow employees to access their own requests or admin/HR to access any.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or getattr(request.user, 'role', None) == 'HR' or getattr(request.user, 'role',
                                                                                               None) == 'Admin':
            return True
        try:
            employee = Employee.objects.get(user=request.user)
            return obj.employee == employee
        except Employee.DoesNotExist:
            return False


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser or getattr(request.user, 'role',None) == 'Admin'


class IsHR(permissions.BasePermission):
    """
    Allows access only to users with role = 'HR'.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'HR'
