from django.db import models
from django.core.validators import RegexValidator



class Employee(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone= models.CharField(max_length=20,validators=[RegexValidator(r'^\+?\d{7,15}$', message="Enter a valid phone number.")])
    address = models.CharField(max_length=255)
    date_joined=models.DateField()
    department = models.ForeignKey('department', on_delete=models.CASCADE)
    job_title=models.ForeignKey('JobTitle',on_delete=models.PROTECT,related_name='employee')
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'employee'

class department(models.Model):
    name=models.CharField(max_length=255)
    

    
class JobTitle(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)


class leaveNote(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    date=models.DateField()
    return_date=models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Leave Note'
        verbose_name_plural = 'Leve Notes'


    
class PayRoll(models.Model):
    name = models.CharField(max_length=255)
    date=models.DateField()
    compensation = models.DecimalField(max_digits=10, decimal_places=2)
    net_pay=models.DecimalField(max_digits=10, decimal_places=2)
    gross_pay=models.DecimalField(max_digits=10, decimal_places=2)
    tax=models.DecimalField(max_digits=10, decimal_places=2)
    bonus=models.DecimalField(max_digits=10, decimal_places=2)
    deductions=models.DecimalField(max_digits=10, decimal_places=2)


