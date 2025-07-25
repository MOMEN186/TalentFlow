from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
    Role_CHOICES = (
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('employee', 'Employee'),
    )
    role = models.CharField(max_length=20, choices=Role_CHOICES)

    def __str__(self):
        return self.username