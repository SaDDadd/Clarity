import os
os.environ['ENV'] = 'test'
import threading
import csv
import random
import asyncio
from locust import HttpUser, task, between, events

# Импортируем truncate_tables вместо drop_tables
from seed_data import truncate_tables


class ClarityUser(HttpUser):
    wait_time = between(0.5, 2)

    @classmethod
    def load_users(cls):
        if not hasattr(cls, 'users'):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(base_dir, 'users.csv')
            with open(csv_path, 'r') as f:
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
            # Сохраняем список проектов, где пользователь – администратор
            resp_projects = self.client.get("/api/v1/projects", headers=self.headers)
            if resp_projects.status_code == 200:
                self.admin_projects = resp_projects.json()
            else:
                self.admin_projects = []
        else:
            raise Exception(f"Login failed for {self.username}")

    @task(3)
    def get_admin_projects(self):
        self.client.get("/api/v1/projects", headers=self.headers)

    @task(2)
    def get_all_projects(self):
        self.client.get("/api/v1/projects/all", headers=self.headers)

    @task(1)
    def create_project(self):
        data = {
            "project_name": f"Load project {random.randint(1,100000)}",
            "project_description": "Created during load test"
        }
        self.client.post("/api/v1/projects", json=data, headers=self.headers)

    @task(1)
    def update_project(self):
        if hasattr(self, 'admin_projects') and self.admin_projects:
            project = random.choice(self.admin_projects)
            data = {
                "project_name": f"Updated {random.randint(1,1000)}",
                "project_description": "Updated description"
            }
            self.client.put(f"/api/v1/projects/{project['project_id']}", json=data, headers=self.headers)

    @task(1)
    def delete_project(self):
        if hasattr(self, 'admin_projects') and self.admin_projects:
            project = random.choice(self.admin_projects)
            self.client.delete(f"/api/v1/projects/{project['project_id']}", headers=self.headers)

    @task(2)
    def get_project_tasks(self):
        resp = self.client.get("/api/v1/projects/all", headers=self.headers)
        if resp.status_code == 200:
            projects = resp.json()
            if projects:
                project = random.choice(projects)
                self.client.get(f"/api/v1/projects/{project['project_id']}/tasks", headers=self.headers)

    @task(1)
    def get_task_detail(self):
        resp = self.client.get("/api/v1/tasks", headers=self.headers)
        if resp.status_code == 200:
            tasks = resp.json()
            if tasks:
                task = random.choice(tasks)
                self.client.get(f"/api/v1/projects/{task['project_id']}/tasks/{task['task_id']}", headers=self.headers)

    @task(1)
    def update_task(self):
        resp = self.client.get("/api/v1/tasks", headers=self.headers)
        if resp.status_code == 200:
            tasks = resp.json()
            if tasks:
                task = random.choice(tasks)
                data = {
                    "title": f"Updated {random.randint(1,1000)}",
                    "task_description": "Updated description"
                }
                self.client.put(f"/api/v1/projects/{task['project_id']}/tasks/{task['task_id']}", json=data, headers=self.headers)

    @task(1)
    def get_invitations(self):
        self.client.get("/api/v1/invitations", headers=self.headers)

    @task(1)
    def create_task(self):
        resp = self.client.get("/api/v1/projects/all", headers=self.headers)
        if resp.status_code == 200:
            projects = resp.json()
            if projects:
                project = random.choice(projects)
                task_data = {
                    "title": f"Load task {random.randint(1,10000)}",
                    "task_description": "Created during load test",
                    "task_status": "pending",
                    "assigned_to": None,
                    "deadline": None
                }
                self.client.post(
                    f"/api/v1/projects/{project['project_id']}/tasks",
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
                statuses = ['pending', 'in_progress', 'completed']
                new_status = random.choice(statuses)
                self.client.patch(
                    f"/api/v1/projects/{task['project_id']}/tasks/{task['task_id']}/status",
                    json={"task_status": new_status},
                    headers=self.headers
                )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("✅ БД уже заполнена вручную. Пропускаем автоматическое заполнение.")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Очистка тестовой БД...")
    truncate_tables()
    print("БД очищена.")