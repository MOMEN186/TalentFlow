from django.db import models

from accounts.models import CustomUser
from employees.models import Employee
# Create your models here.
class LeaveRequest(models.Model):
    LEAVE_TYPES = (('Annual', 'Annual'), ('Sick', 'Sick'), ('Maternity', 'Maternity'), ('Unpaid', 'Unpaid'))
    STATUS_CHOICES = (('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'))

    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='approved_leaves',null=True,blank=True)
    request_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.employee}'