from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status

from TalentFlow.accounts.models import CustomUser
from TalentFlow.api.models import Employee, Department, JobTitle
from .models import Attendance


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


class AttendanceEndpointsTests(APITestCase, AuthMixin):
    def setUp(self):
        self.auth()
        self.dept = Department.objects.create(name="Ops")
        self.job = JobTitle.objects.create(name="Operator")
        self.emp = Employee.objects.create(
            first_name="Att",
            last_name="End",
            middle_name="T",
            gender="Male",
            phone="+20133333333",
            address="C St",
            department=self.dept,
            job_title=self.job,
            status="active",
        )
        from datetime import date
        Attendance.objects.create(employee=self.emp, date=date(2025, 8, 1))

    def test_attendance_list(self):
        url = "/attendance/attendance/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("results", resp.data)

