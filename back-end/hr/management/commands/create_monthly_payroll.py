from django.core.management.base import BaseCommand
from datetime import date
from TalentFlow.api.models import Employee
from hr.models import PayRoll

class Command(BaseCommand):
    help = "Pre-create payroll records for all employees for the current month."

    def handle(self, *args, **kwargs):
        today = date.today()
        year, month = today.year, today.month

        employees = Employee.objects.all()
        created_count = 0

        for emp in employees:
            payroll, created = PayRoll.objects.get_or_create(
                employee=emp,
                year=year,
                month=month,
                defaults={
                    "compensation": emp.salary,  # assuming Employee has salary field
                    "bonus": 0,
                    "deductions": 0,
                    "tax": 0
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Created {created_count} payroll records for {month}/{year}")
        )
