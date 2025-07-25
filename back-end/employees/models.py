from django.db import models
from accounts.models import CustomUser
# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(null=True,blank=True)
    manager = models.OneToOneField(CustomUser,on_delete=models.PROTECT,related_name='managed_department',null=True,blank=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Departments"
        verbose_name_plural = "Departments"

class JobTitle(models.Model):
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Job Titles"
        verbose_name_plural = "Job Titles"

class Employee(models.Model):

    GENDER_CHOICES = (('Male', 'Male'), ('Female', 'Female'))
    MARITAL_CHOICES = (('Single', 'Single'), ('Married', 'Married'), ('Widowed', 'Widowed'), ('Divorced', 'Divorced'))

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=11,unique=True)
    address = models.TextField()
    hire_date = models.DateField()
    national_id = models.CharField(max_length=14,unique=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_CHOICES)
    emergency_contact = models.CharField(max_length=11,null=True,blank=True)
    annual_leave_balance = models.IntegerField()
    is_active = models.BooleanField(default=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT,related_name='employees')
    job_title = models.ForeignKey(JobTitle, on_delete=models.PROTECT,related_name='employees')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
