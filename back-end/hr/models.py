# hr/models.py
from django.db import models

class PayRoll(models.Model):
    employee = models.ForeignKey("api.Employee", on_delete=models.PROTECT, related_name="payrolls")
    year = models.IntegerField()
    month = models.IntegerField()
    compensation = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('employee', 'year', 'month')

    def save(self, *args, **kwargs):
        self.gross_pay = self.compensation + self.bonus
        self.net_pay = self.gross_pay - self.tax - self.deductions
        super().save(*args, **kwargs)


class CompanyPolicy(models.Model):
    late_deduction_per_hour = models.DecimalField(max_digits=6, decimal_places=2, default=10)
    overtime_bonus_per_hour = models.DecimalField(max_digits=6, decimal_places=2, default=15)
    absent_deduction = models.DecimalField(max_digits=6, decimal_places=2, default=100)

    def __str__(self):
        return "Company Policy"
