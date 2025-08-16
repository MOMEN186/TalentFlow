from django.db import models
from django.core.validators import RegexValidator


class Employee(models.Model):
    first_name = models.CharField(max_length=255, null=False, blank=False)
    middle_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female")],
        null=False,
        blank=False,
    )
    
    email = models.EmailField(max_length=255)
    phone= models.CharField(max_length=20,validators=[RegexValidator(r'^\+?\d{7,15}$', message="Enter a valid phone number.")])
    address = models.CharField(max_length=255)
    date_joined=models.DateField(auto_now_add=True)
    department = models.ForeignKey('Department', on_delete=models.PROTECT,related_name='employee')
    job_title=models.ForeignKey('JobTitle',on_delete=models.PROTECT,related_name='employee')
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
    class Meta:
        verbose_name = 'Leave Note'
        verbose_name_plural = 'Leave Notes'


