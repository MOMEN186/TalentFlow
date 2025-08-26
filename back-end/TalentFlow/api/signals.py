# api/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Exit,Employee
from TalentFlow.accounts.models import CustomUser

@receiver(post_save, sender=Exit)
def apply_exit_to_employee(sender, instance: Exit, created, **kwargs):
    if created:
        emp = instance.employee
        # update termination_date if not already set or if new date is later
        if not emp.termination_date or instance.exit_date != emp.termination_date:
            emp.termination_date = instance.exit_date
        # set status (use whatever convention you have)
        emp.status = "inactive"
        emp.save(update_fields=["termination_date", "status"])


@receiver(post_save, sender=CustomUser)
def create_employee_for_user(sender, instance, created, **kwargs):
    if created and (not hasattr(instance, "employee") or instance.is_superuser):
        Employee.objects.create(user=instance)