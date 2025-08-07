from django.db import models
from django.core.validators import RegexValidator



class Employee(models.Model):
    first_name = models.CharField(max_length=255, null=False, blank=False)
    middle_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    gender = models.CharField(
        max_length=10, choices=[("Male", "Male"), ("Female", "Female")]
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


    
class PayRoll(models.Model):
    name = models.CharField(max_length=255)
    date=models.DateField(auto_now_add=True)
    compensation = models.DecimalField(max_digits=10, decimal_places=2)
    net_pay=models.DecimalField(max_digits=10, decimal_places=2)
    gross_pay=models.DecimalField(max_digits=10, decimal_places=2)
    tax=models.DecimalField(max_digits=10, decimal_places=2)
    bonus=models.DecimalField(max_digits=10, decimal_places=2)
    deductions=models.DecimalField(max_digits=10, decimal_places=2)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='payrolls')

    class Meta:
        unique_together = ('employee', 'date')
    def __str__(self):
        return f"{self.name} - {self.date.strftime('%Y-%m-%d')}"

    
    def save(self, *args, **kwargs):
        # Calculate gross and net before saving
        self.gross_pay = self.compensation + self.bonus
        self.net_pay = self.gross_pay - self.tax - self.deductions
        super().save(*args, **kwargs)

