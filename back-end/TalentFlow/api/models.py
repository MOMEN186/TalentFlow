# api/models.py
from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from TalentFlow.accounts.models import CustomUser


class Employee(models.Model):
    user=models.OneToOneField(
      CustomUser, 
        on_delete=models.CASCADE, 
        related_name='employee_profile',
        null=True,
        blank=True)
    first_name = models.CharField(max_length=255, null=False, blank=False)
    middle_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female")],
        null=False,
        blank=False,
    )
    
    
    phone= models.CharField(max_length=20,validators=[RegexValidator(r'^\+?\d{7,15}$', message="Enter a valid phone number.")])
    address = models.CharField(max_length=255)
    date_joined=models.DateField(auto_now_add=True)
    department = models.ForeignKey('Department', on_delete=models.PROTECT,related_name='employee')
    job_title=models.ForeignKey('JobTitle',on_delete=models.PROTECT,related_name='employee')
    termination_date = models.DateField(null=True, blank=True)
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('binding', 'Binding'),
        ('notice', 'On Notice Period'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='binding')
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee')
    def __str__(self):
        return self.first_name
    class Meta:
        db_table = 'employee'

class Department(models.Model):
    name=models.CharField(max_length=255)
    def __str__(self):
        return self.name

class JobTitle(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class LeaveNote(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    date=models.DateField()
    return_date=models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,related_name='leave_note')
    status = models.CharField(
        max_length=255,
        default="Pending",
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Denied", "Denied"),
        ],
    )
    class Meta:
        verbose_name = 'Leave Note'
        verbose_name_plural = 'Leave Notes'


class Exit(models.Model):
    EXIT_TYPE_CHOICES = [
        ("voluntary", "Voluntary"),
        ("involuntary", "Involuntary"),
        ("end_of_contract", "End of contract"),
    ]
    exit_date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT,related_name='exit')
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    exit_type = models.CharField(
        max_length=255,
        choices=EXIT_TYPE_CHOICES
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="recorded_exits"
    )
    final_settlement_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Exit"
        verbose_name_plural = "Exits"
        ordering = ["-exit_date", "-created_at"]

    def __str__(self):
        return f"{self.employee} — {self.get_exit_type_display()} ({self.exit_date})"

    def clean(self):
        # basic validation: can't exit before hire/join date
        if self.employee and self.employee.date_joined and self.exit_date < self.employee.date_joined:
            raise ValidationError("Exit date cannot be earlier than employee's join date.")

    def save(self, *args, **kwargs):
        self.full_clean()  # run clean() -> raises ValidationError if invalid
        super().save(*args, **kwargs)