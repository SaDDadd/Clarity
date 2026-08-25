import csv
import random
from locust import HttpUser, task, between, events

class ClarityUser(HttpUser):
    wait_time = between(0.5, 2)

    @classmethod
    def load_users(cls):
        if not hasattr(cls, 'users'):
            with open('tests/load/users.csv', 'r') as f:
                reader = csv.DictReader(f)
                cls.users = list(reader)
            random.shuffle(cls.users)

    def on_start(self):
        self.load_users()
        user = random.choice(self.__class__.users)
        self.username = user['username']
        self.password = user['password']
        resp = self.client.post("/api/v1/auth/login", json={
            "username_or_email": self.username,
            "password": self.password
        })
        if resp.status_code == 200:
            self.token = resp.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            raise Exception(f"Login failed for {self.username}")

    @task(3)
    def get_admin_projects(self):
        self.client.get("/api/v1/projects", headers=self.headers)

    @task(2)
    def get_all_projects(self):
        self.client.get("/api/v1/projects/all", headers=self.headers)

    @task(1)
    def create_task(self):
        resp = self.client.get("/api/v1/projects/all", headers=self.headers)
        if resp.status_code == 200:
            projects = resp.json()
            if projects:
                project = random.choice(projects)
                project_id = project['project_id']
                task_data = {
                    "title": f"Load task {random.randint(1,10000)}",
                    "task_description": "Created during load test",
                    "task_status": "pending",
                    "assigned_to": None,
                    "deadline": None
                }
                self.client.post(
                    f"/api/v1/projects/{project_id}/tasks",
                    json=task_data,
                    headers=self.headers
                )

    @task(1)
    def get_project_info(self):
        resp = self.client.get("/api/v1/projects/all", headers=self.headers)
        if resp.status_code == 200:
            projects = resp.json()
            if projects:
                project = random.choice(projects)
                self.client.get(f"/api/v1/projects/{project['project_id']}", headers=self.headers)

    @task(1)
    def update_task_status(self):
        resp = self.client.get("/api/v1/tasks", headers=self.headers)
        if resp.status_code == 200:
            tasks = resp.json()
            if tasks:
                task = random.choice(tasks)
                project_id = task['project_id']
                task_id = task['task_id']
                statuses = ['pending', 'in_progress', 'completed']
                new_status = random.choice(statuses)
                self.client.patch(
                    f"/api/v1/projects/{project_id}/tasks/{task_id}/status",
                    json={"task_status": new_status},
                    headers=self.headers
                )