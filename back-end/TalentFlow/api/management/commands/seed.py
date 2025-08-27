# management/commands/seed.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from datetime import datetime, timedelta, time
from django.apps import apps

"""
Seed command tailored to the provided DB schema:
- api.Employee (date_joined DateField auto_now_add=True but we set explicit values)
- api.Exit (exit_date, employee FK, clean() requires exit_date >= employee.date_joined)
- hr.PayRoll (employee FK, unique_together employee/year/month)
- attendance.Attendance (unique_together employee/date)
- api.LeaveNote
- api.Department, api.JobTitle

Features:
- realistic join dates up to 5 years back
- creates Exit rows and sets Employee.termination_date/status
- bulk operations with chunking
- safe deletion order (Exit removed before Employee because Exit.employee on_delete=PROTECT)
"""

def _gen_phone():
    """Generate a phone string compatible with r'^\+?\d{7,15}$'"""
    length = random.randint(9, 12)
    return "+" + "".join(random.choices("0123456789", k=length))

def chunked_iterable(iterable, size):
    """Yield successive chunks of `size` from `iterable`."""
    buf = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

class Command(BaseCommand):
    help = "Seed database with realistic fake data for departments, job titles, employees, payroll, attendance, leave notes and exits."

    def add_arguments(self, parser):
        parser.add_argument("--departments", type=int, default=20, help="Number of departments to create")
        parser.add_argument("--job_titles", type=int, default=50, help="Number of job titles to create")
        parser.add_argument("--employees", type=int, default=3000, help="Number of employees to create")
        parser.add_argument("--leave_notes", type=int, default=200, help="Number of leave notes to create")
        parser.add_argument("--attendance_days", type=int, default=10, help="Number of past days per employee to create attendance for")
        parser.add_argument("--batch_size", type=int, default=1000, help="Bulk create/update batch size")
        parser.add_argument("--exits_rate", type=float, default=0.05, help="Fraction (0.0-1.0) of employees to mark as exited")
        parser.add_argument("--skip_confirm", action="store_true", help="Skip confirmation prompt when deleting existing data")

    def handle(self, *args, **options):
        fake = Faker()
        random.seed(42)

        # Lazy model loading — prevents circular import problems
        try:
            JobTitle = apps.get_model("api", "JobTitle")
            Employee = apps.get_model("api", "Employee")
            LeaveNote = apps.get_model("api", "LeaveNote")
            PayRoll = apps.get_model("hr", "PayRoll")
            Attendance = apps.get_model("attendance", "Attendance")
            Department = apps.get_model("api", "Department")
            Exit = apps.get_model("api", "Exit")
        except LookupError as e:
            self.stderr.write(self.style.ERROR(f"Model lookup failed: {e}. Ensure app labels and model names are correct."))
            return

        # Read choices from model fields (keeps generator aligned with schema)
        try:
            gender_choices = [c[0] for c in Employee._meta.get_field("gender").choices]
            status_choices = [c[0] for c in Employee._meta.get_field("status").choices]
            leave_status_choices = [c[0] for c in LeaveNote._meta.get_field("status").choices]
            exit_type_choices = [c[0] for c in Exit._meta.get_field("exit_type").choices]
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to read choices from models: {e}"))
            return

        # Options
        departments_cnt = options["departments"]
        job_titles_cnt = options["job_titles"]
        employees_cnt = options["employees"]
        leave_notes_cnt = options["leave_notes"]
        attendance_days = options["attendance_days"]
        batch_size = options["batch_size"]
        exits_rate = max(0.0, min(1.0, float(options.get("exits_rate", 0.05))))
        skip_confirm = options["skip_confirm"]

        if not skip_confirm:
            confirm = input(
                "This will DELETE existing LeaveNote, Attendance, PayRoll, Exit, Employee, JobTitle, Department data. Are you sure? [y/N]: "
            )
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Aborted by user."))
                return

        # Clear existing data in safe order: delete dependent objects first
        self.stdout.write("Clearing existing data...")
        LeaveNote.objects.all().delete()       # cascades to nothing else
        Attendance.objects.all().delete()
        PayRoll.objects.all().delete()
        # Exit has PROTECT on employee, so delete exits before employees
        Exit.objects.all().delete()
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

        # Employees — set realistic join dates up to 5 years back
        today = timezone.now().date()
        max_days_back = 365 * 5

        self.stdout.write(f"Creating {employees_cnt} employees...")
        employee_objs = []
        for _ in range(employees_cnt):
            first = fake.first_name()
            middle = fake.first_name()
            last = fake.last_name()
            phone = _gen_phone()
            address = fake.address()[:255]

            # realistic join date in the past (0 .. max_days_back)
            join_date = today - timedelta(days=random.randint(0, max_days_back))

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
                date_joined=join_date,  # override auto_now_add with an explicit join date
                # user left NULL intentionally
            )
            employee_objs.append(emp)

        # Bulk create employees in chunks
        for chunk in chunked_iterable(employee_objs, batch_size):
            Employee.objects.bulk_create(chunk, batch_size=batch_size)

        employees = list(Employee.objects.all())

        # Exits: create a fraction of employees as exited and set termination_date/status
        exits_count = int(len(employees) * exits_rate)
        self.stdout.write(f"Creating {exits_count} exit records (exits_rate={exits_rate})...")

        exit_objs = []
        employees_to_update = []

        if exits_count > 0:
            # choose unique sample
            candidate_emps = random.sample(employees, exits_count)

            for emp in candidate_emps:
                # ensure exit_date >= employee.date_joined
                join = emp.date_joined if getattr(emp, "date_joined", None) else today - timedelta(days=random.randint(30, max_days_back))
                # exit_date between join_date and today
                exit_date = fake.date_between(start_date=join, end_date='today')

                # Compose Exit object — bulk_create will bypass .save().full_clean(), so ensure validity here
                reason = fake.sentence(nb_words=6)[:255]
                ex = Exit(
                    exit_date=exit_date,
                    employee=emp,
                    reason=reason,
                    notes=fake.text(max_nb_chars=200),
                    exit_type=random.choice(exit_type_choices),
                    recorded_by=None,  # leave null
                    final_settlement_amount=round(random.uniform(0, 5000), 2)
                )
                exit_objs.append(ex)

                # update employee termination_date and status locally
                emp.termination_date = exit_date
                if exit_date <= today:
                    emp.status = Employee._meta.get_field("status").choices and "inactive" or emp.status
                employees_to_update.append(emp)

            # Bulk create Exit records in chunks
            for chunk in chunked_iterable(exit_objs, batch_size):
                Exit.objects.bulk_create(chunk, batch_size=batch_size)

            # Bulk update employee termination_date and status
            # Only update fields that exist
            update_fields = []
            try:
                # check field existence
                Employee._meta.get_field('termination_date')
                update_fields.append('termination_date')
            except Exception:
                pass
            try:
                Employee._meta.get_field('status')
                update_fields.append('status')
            except Exception:
                pass

            if update_fields and employees_to_update:
                Employee.objects.bulk_update(employees_to_update, update_fields, batch_size=batch_size)

        # Payrolls (one current month payroll per employee)
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

        # Final counts
        self.stdout.write(self.style.SUCCESS(
            f"Successfully created:\n"
            f"- {Department.objects.count()} departments\n"
            f"- {JobTitle.objects.count()} job titles\n"
            f"- {Employee.objects.count()} employees\n"
            f"- {PayRoll.objects.count()} payrolls\n"
            f"- {Attendance.objects.count()} attendance records\n"
            f"- {LeaveNote.objects.count()} leave notes\n"
            f"- {Exit.objects.count()} exits"
        ))
