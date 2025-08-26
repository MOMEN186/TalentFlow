from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from datetime import datetime, timedelta, time
from django.apps import apps

def _gen_phone():
    """Generate a phone string matching r'^\+?\d{7,15}$' -> + and 9-12 digits."""
    length = random.randint(9, 12)
    return "+" + "".join(random.choices("0123456789", k=length))

def chunked_iterable(iterable, size):
    buf = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

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
        random.seed(42)

        # Lazy model loading to avoid circular import
        try:
            JobTitle = apps.get_model("api", "JobTitle")
            Employee = apps.get_model("api", "Employee")
            LeaveNote = apps.get_model("api", "LeaveNote")
            PayRoll = apps.get_model("hr", "PayRoll")
            Attendance = apps.get_model("attendance", "Attendance")
            Department = apps.get_model("api", "Department")

        except LookupError as e:
            self.stderr.write(self.style.ERROR(f"Model lookup failed: {e}. Ensure app labels and model names are correct."))
            return

        # Derive choices from the model fields (strict to schema)
        try:
            gender_choices = [c[0] for c in Employee._meta.get_field("gender").choices]
            status_choices = [c[0] for c in Employee._meta.get_field("status").choices]
            leave_status_choices = [c[0] for c in LeaveNote._meta.get_field("status").choices]
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to read field choices from models: {e}"))
            return

        departments_cnt = options["departments"]
        job_titles_cnt = options["job_titles"]
        employees_cnt = options["employees"]
        leave_notes_cnt = options["leave_notes"]
        attendance_days = options["attendance_days"]
        batch_size = options["batch_size"]
        skip_confirm = options["skip_confirm"]

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
        for chunk in chunked_iterable(departments, batch_size):
            Department.objects.bulk_create(chunk, batch_size=batch_size)
        departments = list(Department.objects.all())

        # Job Titles
        self.stdout.write(f"Creating {job_titles_cnt} job titles...")
        job_titles = [
            JobTitle(name=fake.job(), description=fake.text(max_nb_chars=200))
            for _ in range(job_titles_cnt)
        ]
        for chunk in chunked_iterable(job_titles, batch_size):
            JobTitle.objects.bulk_create(chunk, batch_size=batch_size)
        job_titles = list(JobTitle.objects.all())

        # Employees
        self.stdout.write(f"Creating {employees_cnt} employees...")
        employee_objs = []
        for _ in range(employees_cnt):
            first = fake.first_name()
            middle = fake.first_name()
            last = fake.last_name()
            phone = _gen_phone()
            address = fake.address()[:255]

            emp = Employee(
                first_name=first,
                middle_name=middle,
                last_name=last,
                gender=random.choice(gender_choices),
                phone=phone,
                address=address,
                department=random.choice(departments),
                job_title=random.choice(job_titles),
                status=random.choice(status_choices),
                # user left NULL to avoid touching CustomUser
            )
            employee_objs.append(emp)

        for chunk in chunked_iterable(employee_objs, batch_size):
            Employee.objects.bulk_create(chunk, batch_size=batch_size)

        employees = list(Employee.objects.all())

        # Payrolls
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

        for chunk in chunked_iterable(payroll_list, batch_size):
            PayRoll.objects.bulk_create(chunk, batch_size=batch_size)

        # Attendance
        self.stdout.write(f"Creating attendance records ({attendance_days} days per employee)...")
        today = timezone.now().date()

        def recent_dates(n, max_back_days=60):
            max_back_days = max(n, max_back_days)
            choices = list(range(0, max_back_days))
            sampled = random.sample(choices, k=n)
            return [today - timedelta(days=d) for d in sampled]

        attendance_buffer = []
        for emp in employees:
            days_for_emp = min(attendance_days, 30)
            dates = recent_dates(days_for_emp, max_back_days=60)

            for date_obj in dates:
                hour = random.randint(8, 9)
                minute = random.randint(0, 59)
                check_in_dt = datetime.combine(date_obj, time(hour, minute))
                check_out_dt = check_in_dt + timedelta(hours=8, minutes=random.randint(0, 59))

                try:
                    check_in_time = timezone.make_aware(check_in_dt)
                    check_out_time = timezone.make_aware(check_out_dt)
                except Exception:
                    check_in_time = check_in_dt
                    check_out_time = check_out_dt

                attendance_buffer.append(Attendance(
                    employee=emp,
                    date=date_obj,
                    check_in=check_in_time,
                    check_out=check_out_time
                ))

            if len(attendance_buffer) >= batch_size:
                Attendance.objects.bulk_create(attendance_buffer, batch_size=batch_size)
                attendance_buffer = []

        if attendance_buffer:
            Attendance.objects.bulk_create(attendance_buffer, batch_size=batch_size)

        # Leave Notes
        self.stdout.write(f"Creating {leave_notes_cnt} leave notes...")
        leave_notes_list = []
        for _ in range(leave_notes_cnt):
            emp = random.choice(employees)
            start_date = fake.date_between(start_date='-30d', end_date='+60d')
            max_return = start_date + timedelta(days=30)
            end_date = fake.date_between(start_date=start_date, end_date=max_return)
            leave_notes_list.append(LeaveNote(
                name=f"{emp.first_name} {emp.last_name}",
                description=fake.text(max_nb_chars=255)[:255],
                date=start_date,
                return_date=end_date,
                employee=emp,
                status=random.choice(leave_status_choices),
            ))

        for chunk in chunked_iterable(leave_notes_list, batch_size):
            LeaveNote.objects.bulk_create(chunk, batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully created:\n"
            f"- {Department.objects.count()} departments\n"
            f"- {JobTitle.objects.count()} job titles\n"
            f"- {Employee.objects.count()} employees\n"
            f"- {PayRoll.objects.count()} payrolls\n"
            f"- {Attendance.objects.count()} attendance records\n"
            f"- {LeaveNote.objects.count()} leave notes"
        ))
