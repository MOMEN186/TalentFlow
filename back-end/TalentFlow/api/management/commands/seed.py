from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from datetime import datetime, timedelta, time

from TalentFlow.api.models import Department, JobTitle, Employee, LeaveNote
from hr.models import PayRoll
from attendance.models import Attendance


class Command(BaseCommand):
    help = "Seed database with realistic fake data for departments, job titles, employees, payroll, attendance and leave notes."

    def add_arguments(self, parser):
        parser.add_argument("--departments", type=int, default=20, help="Number of departments to create")
        parser.add_argument("--job_titles", type=int, default=50, help="Number of job titles to create")
        parser.add_argument("--employees", type=int, default=3000, help="Number of employees to create")
        parser.add_argument("--leave_notes", type=int, default=200, help="Number of leave notes to create")
        parser.add_argument("--attendance_days", type=int, default=10, help="Number of past days per employee to create attendance for")
        parser.add_argument("--batch_size", type=int, default=1000, help="Bulk create batch size")
        parser.add_argument("--skip_confirm", action="store_true", help="Skip confirmation prompt when deleting existing data")

    def handle(self, *args, **options):
        fake = Faker()
        departments_cnt = options["departments"]
        job_titles_cnt = options["job_titles"]
        employees_cnt = options["employees"]
        leave_notes_cnt = options["leave_notes"]
        attendance_days = options["attendance_days"]
        batch_size = options["batch_size"]
        skip_confirm = options["skip_confirm"]

        # Confirmation before destructive operation
        if not skip_confirm:
            confirm = input(
                "This will DELETE existing LeaveNote, Attendance, PayRoll, Employee, JobTitle, Department data. Are you sure? [y/N]: "
            )
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Aborted by user."))
                return

        self.stdout.write("Clearing existing data...")
        LeaveNote.objects.all().delete()
        Attendance.objects.all().delete()
        PayRoll.objects.all().delete()
        Employee.objects.all().delete()
        JobTitle.objects.all().delete()
        Department.objects.all().delete()

        # Departments
        self.stdout.write(f"Creating {departments_cnt} departments...")
        departments = [Department(name=fake.unique.company()) for _ in range(departments_cnt)]
        Department.objects.bulk_create(departments, batch_size=batch_size)
        departments = list(Department.objects.all())

        # Job Titles
        self.stdout.write(f"Creating {job_titles_cnt} job titles...")
        job_titles = [JobTitle(name=fake.job(), description=fake.text(max_nb_chars=200)) for _ in range(job_titles_cnt)]
        JobTitle.objects.bulk_create(job_titles, batch_size=batch_size)
        job_titles = list(JobTitle.objects.all())

        # Employees
        self.stdout.write(f"Creating {employees_cnt} employees...")
        employee_objs = []
        for _ in range(employees_cnt):
            emp = Employee(
                first_name=fake.first_name(),
                middle_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                phone=str(fake.phone_number())[:20],
                address=fake.address(),
                department=random.choice(departments),
                job_title=random.choice(job_titles),
            )
            employee_objs.append(emp)

        Employee.objects.bulk_create(employee_objs, batch_size=batch_size)
        employees = list(Employee.objects.all())

        # Payrolls - one payroll row per employee for current month
        self.stdout.write("Creating payrolls...")
        payroll_list = []
        now = timezone.now()
        for emp in employees:
            compensation = round(random.uniform(3000, 10000), 2)
            bonus = round(random.uniform(100, 1000), 2)
            tax = round(random.uniform(100, 500), 2)
            deductions = round(random.uniform(50, 800), 2)

            gross_pay = compensation + bonus
            net_pay = gross_pay - tax - deductions

            payroll_list.append(PayRoll(
                employee=emp,
                year=now.year,
                month=now.month,
                compensation=compensation,
                gross_pay=gross_pay,
                net_pay=net_pay,
                bonus=bonus,
                deductions=deductions,
                tax=tax
            ))

        PayRoll.objects.bulk_create(payroll_list, batch_size=batch_size)

        # Attendance - create up to `attendance_days` unique dates per employee
        self.stdout.write(f"Creating attendance records ({attendance_days} days per employee)...")
        attendance_records = []
        today = timezone.now().date()

        # Helper: generate a list of unique recent dates (skipping duplicates)
        def recent_dates(n, max_back_days=60):
            # pick `n` unique days from the last `max_back_days`
            max_back_days = max(n, max_back_days)
            choices = list(range(0, max_back_days))
            sampled = random.sample(choices, k=n)
            return [today - timedelta(days=d) for d in sampled]

        for emp in employees:
            # pick unique dates for this employee
            days_for_emp = min(attendance_days, 30)
            dates = recent_dates(days_for_emp, max_back_days=60)

            for date_obj in dates:
                # make check-in time between 08:00 and 09:59 to avoid wide spread
                hour = random.randint(8, 9)
                minute = random.randint(0, 59)
                check_in_dt = datetime.combine(date_obj, time(hour, minute))
                check_out_dt = check_in_dt + timedelta(hours=8, minutes=random.randint(0, 59))

                # make timezone-aware datetimes (works when USE_TZ = True)
                try:
                    check_in_time = timezone.make_aware(check_in_dt)
                    check_out_time = timezone.make_aware(check_out_dt)
                except Exception:
                    # fallback if already aware or other issues
                    check_in_time = check_in_dt
                    check_out_time = check_out_dt

                attendance_records.append(Attendance(
                    employee=emp,
                    date=date_obj,
                    check_in=check_in_time,
                    check_out=check_out_time
                ))

        Attendance.objects.bulk_create(attendance_records, batch_size=batch_size)

        # Leave Notes
        self.stdout.write(f"Creating {leave_notes_cnt} leave notes...")
        leave_notes_list = []
        for _ in range(leave_notes_cnt):
            emp = random.choice(employees)
            start_date = fake.date_between(start_date='-30d', end_date='+60d')
            end_date = fake.date_between(start_date=start_date, end_date=start_date + timedelta(days=30))
            leave_notes_list.append(LeaveNote(
                name=fake.name(),
                description=fake.text(max_nb_chars=255),
                date=start_date,
                return_date=end_date,
                employee=emp
            ))

        LeaveNote.objects.bulk_create(leave_notes_list, batch_size=batch_size)

        # Done
        self.stdout.write(self.style.SUCCESS(
            f"Successfully created:\n"
            f"- {Department.objects.count()} departments\n"
            f"- {JobTitle.objects.count()} job titles\n"
            f"- {Employee.objects.count()} employees\n"
            f"- {PayRoll.objects.count()} payrolls\n"
            f"- {Attendance.objects.count()} attendance records\n"
            f"- {LeaveNote.objects.count()} leave notes"
        ))
