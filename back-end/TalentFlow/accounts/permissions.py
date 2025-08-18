# accounts/permissions.py
from rest_framework.permissions import BasePermission

class IsHRUser(BasePermission):
    """
    Allow access only to authenticated users who are:
      - superuser (always allowed), or
      - staff (optional convenience), or
      - member of the 'HR' group, or
      - have an 'is_hr' attribute set True on their user model (optional custom flag).
    Adjust logic to your needs.
    """
    message = "You must be an HR user to access this resource."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        # Always allow superusers
        if getattr(user, "is_superuser", False):
            return True

        # Optionally allow staff users (remove if you don't want this)
        if getattr(user, "is_staff", False):
            return True

        # Group-based check (PermissionsMixin provides groups)
        try:
            if user.groups.filter(name="HR").exists():
                return True
        except Exception:
            # if groups not configured for your user model, ignore
            pass

        # Optional: allow a custom boolean field on the user model
        if getattr(user, "is_hr", False):
            return True

        return False
