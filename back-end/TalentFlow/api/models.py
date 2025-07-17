from django.db import models
from django.core.validators import RegexValidator



class employee(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone= models.CharField(max_length=20,validators=[RegexValidator(r'^\+?\d{7,15}$', message="Enter a valid phone number.")])
    address = models.CharField(max_length=255)
    date_joined=models.DateField()
    department = models.ForeignKey('department', on_delete=models.CASCADE)
    
class department(models.Model):
    name=models.CharField(max_length=255)
    

    
class JobTitle(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    employee = models.OneToOneField(employee, on_delete=models.CASCADE)


class leve_note(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    date=models.DateField()
    return_date=models.DateField()
    employee = models.ForeignKey(employee, on_delete=models.CASCADE)
    
    
class pay_roll(models.Model):
    name = models.CharField(max_length=255)
    date=models.DateField()
    employee = models.ForeignKey(employee, on_delete=models.CASCADE)
    compensation = models.DecimalField(max_digits=10, decimal_places=2)
    net_pay=models.DecimalField(max_digits=10, decimal_places=2)
    gross_pay=models.DecimalField(max_digits=10, decimal_places=2)
    tax=models.DecimalField(max_digits=10, decimal_places=2)
    bonus=models.DecimalField(max_digits=10, decimal_places=2)
    deductions=models.DecimalField(max_digits=10, decimal_places=2)


