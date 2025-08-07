# api/management/commands/seed.py

from django.core.management.base import BaseCommand
from faker import Faker
import random
from TalentFlow.api.models import Department, JobTitle, PayRoll, Employee, LeaveNote

departments_cnt = 20
job_titles_cnt = 50
payrolls_cnt = 3000  # Reduced to match employees (one per employee)
employees_cnt = 3000
leave_notes_cnt = 200

class Command(BaseCommand):
    help = 'Seed database with fake data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Clear existing data to avoid unique constraint violations
        self.stdout.write("Clearing existing data...")
        LeaveNote.objects.all().delete()
        PayRoll.objects.all().delete()
        Employee.objects.all().delete()
        JobTitle.objects.all().delete()
        Department.objects.all().delete()

        # Create Departments using bulk_create
        self.stdout.write("Creating departments...")
        departments_list = []
        for _ in range(departments_cnt):
            departments_list.append(Department(name=fake.word().capitalize()))
        departments = Department.objects.bulk_create(departments_list)

        # Create Job Titles using bulk_create
        self.stdout.write("Creating job titles...")
        job_titles_list = []
        for _ in range(job_titles_cnt):
            job_titles_list.append(JobTitle(name=fake.job(), description=fake.text()))
        job_titles = JobTitle.objects.bulk_create(job_titles_list)

        # Refresh from database to get IDs
        departments = list(Department.objects.all())
        job_titles = list(JobTitle.objects.all())

        # Create Employees using bulk_create
        self.stdout.write("Creating employees...")
        employees_list = []
        for _ in range(employees_cnt):
            employees_list.append(Employee(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                middle_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number()[:20],
                address=fake.address(),
                department=random.choice(departments),
                job_title=random.choice(job_titles),
            ))
        
        # Use batch_size for very large datasets
        Employee.objects.bulk_create(employees_list, batch_size=1000)
        employees = list(Employee.objects.all())

        # Create Payrolls using bulk_create (one per employee to avoid unique constraint)
        self.stdout.write("Creating payrolls...")
        payrolls_list = []
        
        # Get today's date (what auto_now_add will set)
        from django.utils import timezone
        today = timezone.now().date()
        
        # Get employees who don't already have a payroll for today
        existing_payroll_employees = set(
            PayRoll.objects.filter(date=today).values_list('employee_id', flat=True)
        )
        
        available_employees = [emp for emp in employees if emp.id not in existing_payroll_employees]
        
        for employee in available_employees[:payrolls_cnt]:
            compensation = round(random.uniform(3000, 10000), 2)
            tax = round(random.uniform(100, 500), 2)
            bonus = round(random.uniform(100, 1000), 2)
            deductions = round(random.uniform(50, 800), 2)
            
            # Calculate gross_pay and net_pay manually (same logic as in your model's save method)
            gross_pay = compensation + bonus
            net_pay = gross_pay - tax - deductions
            
            payrolls_list.append(PayRoll(
                name=fake.month_name(),
                compensation=compensation,
                net_pay=net_pay,
                gross_pay=gross_pay,
                tax=tax,
                bonus=bonus,
                deductions=deductions,
                employee=employee
            ))
        
        if payrolls_list:
            PayRoll.objects.bulk_create(payrolls_list, batch_size=1000)
            self.stdout.write(f"Created {len(payrolls_list)} new payroll records")
        else:
            self.stdout.write("No new payroll records needed - all employees already have payrolls for today")

        # Create Leave Notes using bulk_create
        self.stdout.write("Creating leave notes...")
        leave_notes_list = []
        for _ in range(leave_notes_cnt):
            start_date = fake.date_between(start_date='-30d', end_date='+60d')
            return_date = fake.date_between(start_date=start_date, end_date='+90d')
            leave_notes_list.append(LeaveNote(
                name=fake.name(),
                description=fake.text()[:255],  # Ensure it fits in CharField
                date=start_date,
                return_date=return_date,
                employee=random.choice(employees)
            ))
        LeaveNote.objects.bulk_create(leave_notes_list, batch_size=1000)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully created:\n"
            f"- {len(departments)} departments\n"
            f"- {len(job_titles)} job titles\n"
            f"- {employees_cnt} employees\n"
            f"- {len(payrolls_list)} payrolls\n"
            f"- {leave_notes_cnt} leave notes"
        ))