from django.utils.timezone import now
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status

from TalentFlow.accounts.models import CustomUser
from TalentFlow.api.models import Employee, Department, JobTitle, Exit


class AuthMixin:
    email = "momenehab186@gmail.com"
    password = "admin"

    def auth(self):
        user, _ = CustomUser.objects.get_or_create(email=self.email)
        user.set_password(self.password)
        user.is_active = True
        user.is_staff = True
        user.save()
        hr_group, _ = Group.objects.get_or_create(name="HR")
        user.groups.add(hr_group)
        resp = self.client.post("/api/auth/login/", {"email": self.email, "password": self.password}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
        return user


class ReportsTurnoverTests(APITestCase, AuthMixin):
    def setUp(self):
        self.auth()
        self.dept = Department.objects.create(name="BI")
        self.job = JobTitle.objects.create(name="Analyst")
        self.emp = Employee.objects.create(
            first_name="Rep",
            last_name="Ort",
            middle_name="S",
            gender="Male",
            phone="+20144444444",
            address="D St",
            department=self.dept,
            job_title=self.job,
            status="active",
        )

    def test_turnover_report(self):
        Exit.objects.create(employee=self.emp, exit_date=now().date(), reason="Layoff", exit_type="involuntary")
        url = "/reports/turnover/?start=2025-08-01&end=2025-08-31"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("hires_total", resp.data)
        self.assertIn("exits_total", resp.data)
        self.assertIn("attrition_rate_percent", resp.data)

