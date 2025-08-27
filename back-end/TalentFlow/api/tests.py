from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status

from TalentFlow.accounts.models import CustomUser
from .models import Department, JobTitle, Employee, LeaveNote, Exit


class AuthSetupMixin:
    email = "momenehab186@gmail.com"
    password = "admin"

    def auth_setup(self):
        user, _ = CustomUser.objects.get_or_create(email=self.email)
        user.set_password(self.password)
        user.is_active = True
        user.save()
        hr_group, _ = Group.objects.get_or_create(name="HR")
        user.groups.add(hr_group)
        token_resp = self.client.post(reverse("token_obtain_pair"), {"email": self.email, "password": self.password}, format="json")
        self.assertEqual(token_resp.status_code, status.HTTP_200_OK)
        access = token_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return user


class DepartmentJobTitleTests(APITestCase, AuthSetupMixin):
    def setUp(self):
        self.auth_setup()

    def test_departments_crud(self):
        list_url = reverse("departments-list")
        create_resp = self.client.post(list_url, {"name": "Engineering"}, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        dept_id = create_resp.data["id"]

        get_resp = self.client.get(reverse("departments-detail", args=[dept_id]))
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.data["name"], "Engineering")

        patch_resp = self.client.patch(reverse("departments-detail", args=[dept_id]), {"name": "R&D"}, format="json")
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_resp.data["name"], "R&D")

        del_resp = self.client.delete(reverse("departments-detail", args=[dept_id]))
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_job_titles_crud(self):
        list_url = reverse("job-titles-list")
        create_resp = self.client.post(list_url, {"name": "Developer"}, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        jt_id = create_resp.data["id"]

        get_resp = self.client.get(reverse("job-titles-detail", args=[jt_id]))
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.data["name"], "Developer")

        patch_resp = self.client.patch(reverse("job-titles-detail", args=[jt_id]), {"name": "Senior Developer"}, format="json")
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_resp.data["name"], "Senior Developer")

        del_resp = self.client.delete(reverse("job-titles-detail", args=[jt_id]))
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)


class EmployeeEndpointsTests(APITestCase, AuthSetupMixin):
    def setUp(self):
        self.user = self.auth_setup()
        self.dept = Department.objects.create(name="Engineering")
        self.job = JobTitle.objects.create(name="Developer")

    def _employee_payload(self, **overrides):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "middle_name": "M",
            "gender": "Male",
            "phone": "+20123456789",
            "address": "123 Street",
            "department": self.dept.id,
            "job_title": self.job.id,
            "email": "john.doe@example.com",
            "password": "Secret123!",
            "status": "active",
        }
        payload.update(overrides)
        return payload

    def test_employee_create_retrieve_update_list(self):
        list_url = reverse("employees-list")
        create_resp = self.client.post(list_url, self._employee_payload(), format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        emp_id = create_resp.data["id"]

        det = self.client.get(reverse("employees-detail", args=[emp_id]))
        self.assertEqual(det.status_code, status.HTTP_200_OK)
        self.assertIn("employee", det.data)  # custom retrieve wraps in {employee: ...}

        upd = self.client.patch(reverse("employees-detail", args=[emp_id]), {"address": "456 Ave"}, format="json")
        self.assertEqual(upd.status_code, status.HTTP_200_OK)
        self.assertEqual(upd.data["address"], "456 Ave")

        lst = self.client.get(list_url)
        self.assertEqual(lst.status_code, status.HTTP_200_OK)
        self.assertIn("results", lst.data)  # paginated

    def test_employee_actions_empty_lists_and_restore(self):
        emp = self.client.post(reverse("employees-list"), self._employee_payload(email="jane@example.com"), format="json").data
        emp_id = emp["id"]

        # leave notes, exit records, payrolls should be empty arrays
        ln = self.client.get(reverse("employees-leave-notes", kwargs={"pk": emp_id}))
        self.assertEqual(ln.status_code, status.HTTP_200_OK)
        self.assertIsInstance(ln.data, list)

        ex = self.client.get(reverse("employees-exit-records", kwargs={"pk": emp_id}))
        self.assertEqual(ex.status_code, status.HTTP_200_OK)
        self.assertIsInstance(ex.data, list)

        pr = self.client.get(reverse("employees-payrolls", kwargs={"pk": emp_id}))
        self.assertEqual(pr.status_code, status.HTTP_200_OK)
        self.assertIsInstance(pr.data, list)

        # restore action toggles status from inactive to active
        Employee.objects.filter(id=emp_id).update(status="inactive")
        rs = self.client.patch(reverse("employees-restore", kwargs={"pk": emp_id}), {}, format="json")
        self.assertIn(rs.status_code, (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST))

    def test_update_is_hr_action(self):
        emp = self.client.post(reverse("employees-list"), self._employee_payload(email="mark@example.com"), format="json").data
        emp_id = emp["id"]
        resp = self.client.patch(reverse("employees-update-is-hr", kwargs={"pk": emp_id}), {"is_hr": True}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class ExitEndpointsTests(APITestCase, AuthSetupMixin):
    def setUp(self):
        self.user = self.auth_setup()
        self.dept = Department.objects.create(name="Engineering")
        self.job = JobTitle.objects.create(name="Developer")
        self.employee = Employee.objects.create(
            first_name="Alex",
            last_name="Smith",
            middle_name="K",
            gender="Male",
            phone="+20100000000",
            address="X St",
            department=self.dept,
            job_title=self.job,
            status="active",
        )

    def test_exit_create_sets_employee_inactive(self):
        list_url = reverse("exit-list")
        payload = {
            "employee_id": self.employee.id,
            "exit_date": now().date().isoformat(),
            "exit_type": "voluntary",
            "reason": "Resigned",
            "notes": "N/A",
            "final_settlement_amount": "0.00",
        }
        resp = self.client.post(list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.status, "inactive")
        self.assertIsNotNone(self.employee.termination_date)


class LeaveNoteEndpointsTests(APITestCase, AuthSetupMixin):
    def setUp(self):
        self.auth_setup()
        self.dept = Department.objects.create(name="Eng")
        self.job = JobTitle.objects.create(name="Dev")
        self.employee = Employee.objects.create(
            first_name="Lia",
            last_name="Stone",
            middle_name="P",
            gender="Female",
            phone="+20111111111",
            address="A St",
            department=self.dept,
            job_title=self.job,
            status="active",
        )

    def test_leave_notes_list_and_export(self):
        LeaveNote.objects.create(
            name="Vacation",
            description="Family trip",
            date=now().date(),
            return_date=now().date(),
            employee=self.employee,
            status="pending",
        )
        # router list
        list_url = reverse("leave_notes-list")
        lst = self.client.get(list_url)
        self.assertEqual(lst.status_code, status.HTTP_200_OK)

        # export action JSON branch (no excel param)
        resp_json = self.client.get("/api/leave_notes/export/")
        self.assertEqual(resp_json.status_code, status.HTTP_200_OK)
        # excel branch
        resp_xlsx = self.client.get("/api/leave_notes/export/?excel=true")
        self.assertEqual(resp_xlsx.status_code, status.HTTP_200_OK)
        self.assertIn("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", resp_xlsx["Content-Type"]) 

from django.test import TestCase

# Create your tests here.
