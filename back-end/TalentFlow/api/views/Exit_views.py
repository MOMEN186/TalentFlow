# api/viewsets.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import Exit
from ..serializers import ExitSerializer
from TalentFlow.accounts.permissions import IsHRUser  # make sure this path matches your project

class ExitViewSet(viewsets.ModelViewSet):
    """
    CRUD for Exit model.
    - create(): sets recorded_by=request.user
    - after create, we also update employee.termination_date and employee.status to 'inactive'
      (if you already have a signal doing this it's still safe; this keeps API behavior explicit).
    """
    queryset = Exit.objects.select_related("employee", "recorded_by").all()
    serializer_class = ExitSerializer
    permission_classes = [IsAuthenticated, IsHRUser]

    def perform_create(self, serializer):
        # Set recorded_by to the authenticated user
        exit_obj = serializer.save(recorded_by=self.request.user)
        # Update related employee termination info
        emp = exit_obj.employee
        should_update = False
        if not emp.termination_date or emp.termination_date != exit_obj.exit_date:
            emp.termination_date = exit_obj.exit_date
            should_update = True
        # set employee status to inactive (adjust string to your project's convention if needed)
        if emp.status != "inactive":
            emp.status = "inactive"
            should_update = True
        if should_update:
            emp.save(update_fields=["termination_date", "status"])

    def create(self, request, *args, **kwargs):
        # Use default create, but return 201 with serializer data
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Let update happen, then ensure employee termination/status consistency
        response = super().update(request, *args, **kwargs)
        # refresh instance
        if response.status_code in (200, 201):
            try:
                instance = self.get_object()
                emp = instance.employee
                # align employee termination_date/status with exit instance
                should_update = False
                if emp.termination_date != instance.exit_date:
                    emp.termination_date = instance.exit_date
                    should_update = True
                if emp.status != "inactive":
                    emp.status = "inactive"
                    should_update = True
                if should_update:
                    emp.save(update_fields=["termination_date", "status"])
            except Exception:
                pass
        return response
