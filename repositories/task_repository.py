import pymysql 
from db.connection_manager import DatabaseHelper 
from models.task import Task

class TaskRepository:
    def __init__(self):
        self.db_helper = DatabaseHelper()

    def create_task(self, title, description, status, \
                    proj_id, assigned_to, deadline): # Создание задачи
        sql = 'INSERT INTO tasks(title, task_description, task_status, project_id, assigned_to, deadline)' \
        'VALUES (%s, %s, %s, %s, %s, %s)'
        return self.db_helper.execute_query(sql, (title, description,\
                                                  status, proj_id, assigned_to, \
                                                    deadline))

    def get_tasks_by_user(self, assigned_to): # Выбрать все задачи пользователя вместе со статусом задачи
        sql = 'SELECT * FROM tasks ' \
        'WHERE assigned_to = (%s)'
        row = self.db_helper.fetch_all(sql, (assigned_to,))
        return [Task.from_dict(item) for item in row]

    def assign_task(self, user_id, task_id): # Обновление выполняющего задачи
        sql = 'UPDATE tasks SET assigned_to = (%s) WHERE task_id = (%s)'
        return self.db_helper.execute_query(sql, (user_id, task_id))

    def delete_task(self, task_id): # Удаление задачи
        sql = 'DELETE FROM tasks WHERE task_id = (%s)'
        return self.db_helper.execute_query(sql, (task_id,))

    def update_task_all(self, task_id, title, description, status, \
                        project_id, assigned_to): # Обновление задачи
        sql = 'UPDATE tasks SET title = (%s), task_description = (%s), task_status = (%s),' \
        'assigned_to = (%s)' \
        'WHERE task_id = (%s)'
        return self.db_helper.execute_query(sql, (title, description, status, assigned_to, \
                                                  task_id))

    def get_task_by_id(self, task_id): # Поиск задачи по id
        sql = 'SELECT * FROM tasks WHERE task_id = (%s)'
        row = self.db_helper.fetch_one(sql, (task_id,))
        return Task.from_dict_or_none(row)

    def get_task_by_title(self, title): # Посик задачи по имени
        sql = 'SELECT * FROM tasks WHERE title = (%s)'
        row = self.db_helper.fetch_one(sql, (title,))
        return [Task.from_dict_or_none(row)]

    def update_task_by_id(self, task_id, status): # Обновление статуса задачи
        sql = 'UPDATE tasks SET task_status = (%s) WHERE task_id = (%s)'
        return self.db_helper.execute_query(sql, (status, task_id))