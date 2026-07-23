import datetime
from db.connection_manager import DatabaseHelper 
from models.task import Task
from decorators.decorators import log

# Переписать под SQLAlchemy

class TaskRepository:
    def __init__(self) -> None: # Инициализация с подключением к БД
        self.db_helper = DatabaseHelper()

    @log
    def create_task(self, title: str, description: str | None, status: str,
                    proj_id: int, assigned_to: int | None, 
                    deadline: datetime.date | None) -> int | None: # Создать задачу
        sql = 'INSERT INTO tasks(title, task_description, task_status, project_id, assigned_to, deadline)' \
        'VALUES (%s, %s, %s, %s, %s, %s)'
        return self.db_helper.execute_query(sql, (title, description,status, proj_id, 
                                                  assigned_to, deadline))

    @log
    def get_tasks_by_user(self, assigned_to: int) -> list[Task]: # Получить все задачи 
        # пользователя
        sql = 'SELECT * FROM tasks ' \
        'WHERE assigned_to = (%s)'
        row = self.db_helper.fetch_all(sql, (assigned_to,))
        return [Task.from_dict(item) for item in row]

    @log
    def assign_task(self, user_id: int, task_id: int) -> int | None: # Назначить задачу 
        # пользователю
        sql = 'UPDATE tasks SET assigned_to = (%s) WHERE task_id = (%s)'
        return self.db_helper.execute_query(sql, (user_id, task_id))

    def delete_task(self, task_id: int) -> int | None: # Удалить задачу
        sql = 'DELETE FROM tasks WHERE task_id = (%s)'
        return self.db_helper.execute_query(sql, (task_id,))

    @log
    def get_task_by_id(self, task_id: int) -> Task | None: # Получить задачу по ID
        sql = 'SELECT * FROM tasks WHERE task_id = (%s)'
        row = self.db_helper.fetch_one(sql, (task_id,))
        return Task.from_dict_or_none(row)

    @log
    def update_task_by_id(self, task_id: int, status: str) -> int | None: # Обновить статус 
        # задачи
        sql = 'UPDATE tasks SET task_status = (%s) WHERE task_id = (%s)'
        return self.db_helper.execute_query(sql, (status, task_id))