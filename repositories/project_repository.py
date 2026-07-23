from db.connection_manager import DatabaseHelper
from models.project import Project
from decorators.decorators import log

# Переписать под SQLAlchemy

class ProjectRepository:
    def __init__(self) -> None: # Инициализация с подключением к БД
        self.db_helper = DatabaseHelper()

    @log
    def get_projects_by_admin(self, admin_id: int) -> list[Project]: # Получить все проекты 
        # админа
        sql = 'SELECT * FROM projects WHERE admin_id = (%s)'
        row = self.db_helper.fetch_all(sql, (admin_id,))
        return [Project.from_dict(item) for item in row]

    @log
    def update_project_description(self, new_description: str, project_id: int) -> int | None: 
        # Обновить описание проекта
        sql = 'UPDATE projects SET project_description = (%s) WHERE project_id = (%s)'
        return self.db_helper.execute_query(sql, (new_description, project_id))

    def is_user_in_project(self, project_id: int, user_id: int) -> bool: # Проверить, состоит 
        # ли пользователь в проекте
        sql = 'SELECT user_id FROM project_members  WHERE project_id = (%s) AND user_id = (%s)'
        row = self.db_helper.fetch_one(sql, (project_id, user_id))
        if not row:
            return False
        else:
            return True

    @log
    def create_project_with_admin(self, name: str, description: str, admin_id: int, 
                                  role: str) -> list[int] | None: # Создать проект и добавить 
                                                                # админа
        sql_create_project = 'INSERT INTO projects (project_name, project_description, \
            admin_id)' \
            'VALUES (%s, %s, %s)'
        sql_add_user_to_project = 'INSERT INTO project_members (project_id, user_id, role_project)' \
        'VALUES (LAST_INSERT_ID(), %s, %s)'
        result = self.db_helper.execute_transactions(((sql_create_project,(name, description, admin_id)), \
                                             (sql_add_user_to_project, (admin_id, role))))
        return result

    @log
    def get_user_role_in_project(self, project_id: int, user_id: int) -> str | None: # Получить 
        # роль пользователя в проекте
        sql = 'SELECT role_project FROM project_members WHERE project_id = (%s) AND user_id = (%s)'
        row = self.db_helper.fetch_one(sql, (project_id, user_id))
        if not row:
            return None
        return row['role_project']

    @log
    def get_project_by_id(self, project_id: int) -> Project | None: # Получить проект по ID
        sql = 'SELECT * FROM projects WHERE project_id = (%s)'
        row = self.db_helper.fetch_one(sql, (project_id,))
        return Project.from_dict_or_none(row)