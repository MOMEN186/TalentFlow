from locust import HttpUser, task, between

class TalentFlowUser(HttpUser):
    def on_start(self):
        # Login and fetch JWT token
        response = self.client.post("/api/auth/login/", json={
            "email": "momenehab186@gmail.com",
            "password": "admin"
        })
        if response.status_code == 200:
            token = response.json()["access"]
            self.client.headers = {
                "Authorization": f"Bearer {token}"
            }
        else:
            print("Login failed:", response.text)

    wait_time = between(1, 3)

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
        self.client.get("/reports/")
        
    @task
    def get_payroll(self):
        self.client.get("/hr/payroll/")


