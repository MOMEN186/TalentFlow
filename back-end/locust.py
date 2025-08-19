import csv
import random
from locust import HttpUser, task, between

# Load all users into memory once
with open("users.csv", newline="") as f:
    reader = csv.DictReader(f)
    USERS = list(reader)

class TalentFlowUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Pick a random user from CSV
        user = random.choice(USERS)
        response = self.client.post("/api/auth/login/", json={
            "email": user["email"],
            "password": user["password"]
        })
        if response.status_code == 200:
            token = response.json()["access"]
            self.client.headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"Login failed for {user['email']}: {response.text}")

    @task
    def get_employees(self):
        self.client.get("/api/employees/")

    @task
    def get_leaveNotes(self):
        self.client.get("/api/leave_notes/")

    @task
    def get_attendance(self):
        self.client.get("/attendance/attendance/")

    @task
    def get_reports(self):
        self.client.get("/reports/turnover/")

    @task
    def get_payroll(self):
        self.client.get("/hr/payroll/")
