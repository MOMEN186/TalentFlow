from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status

from TalentFlow.accounts.models import CustomUser
from TalentFlow.api.models import Employee, Department, JobTitle
from .models import PayRoll


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


class PayrollEndpointsTests(APITestCase, AuthMixin):
    def setUp(self):
        self.auth()
        self.dept = Department.objects.create(name="Finance")
        self.job = JobTitle.objects.create(name="Analyst")
        self.emp = Employee.objects.create(
            first_name="Pay",
            last_name="Roll",
            middle_name="X",
            gender="Male",
            phone="+20122222222",
            address="B St",
            department=self.dept,
            job_title=self.job,
            status="active",
        )
        PayRoll.objects.create(employee=self.emp, year=2025, month=8, compensation=1000, bonus=100, deductions=50, tax=0)

    def test_payroll_list_and_filters(self):
        url = "/hr/payroll/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("results", resp.data)

        resp_y = self.client.get(url + "?year=2025")
        self.assertEqual(resp_y.status_code, status.HTTP_200_OK)

        resp_m = self.client.get(url + "?month=8")
        self.assertEqual(resp_m.status_code, status.HTTP_200_OK)

