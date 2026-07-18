from db.connection_manager import DatabaseHelper
from models.project import Project

class ProjectRepository:
    def __init__(self):
        self.db_helper = DatabaseHelper()

    def get_projects_by_admin(self, admin_id): # Вывод всех проектов прикрепленных к администратору
        sql = 'SELECT * FROM projects WHERE admin_id = (%s)'
        row = self.db_helper.fetch_all(sql, (admin_id,))
        return [Project.from_dict(item) for item in row]

    def update_project_description(self, new_description, project_id): # Обновление описания проекта
        sql = 'UPDATE projects SET project_description = (%s) WHERE project_id = (%s)'
        return self.db_helper.execute_query(sql, (new_description, project_id))

    def is_user_in_project(self, project_id, user_id): # Проверка на существование пользователя в проекте (возращаем true/false)
        sql = 'SELECT user_id FROM project_members  WHERE project_id = (%s) AND user_id = (%s)'
        row = self.db_helper.fetch_one(sql, (project_id, user_id))
        if not row:
            return False
        else:
            return True

    def create_project_with_admin(self, name, description, admin_id, role): # Создание проекта и добавление админа в проект
        sql_create_project = 'INSERT INTO projects (project_name, project_description, \
            admin_id)' \
            'VALUES (%s, %s, %s)'
        sql_add_user_to_project = 'INSERT INTO project_members (project_id, user_id, role_project)' \
        'VALUES (LAST_INSERT_ID(), %s, %s)'
        result = self.db_helper.execute_transactions(((sql_create_project,(name, description, admin_id)), \
                                             (sql_add_user_to_project, (admin_id, role))))
        return result

    def get_user_role_in_project(self, project_id, user_id): # Вывод роли пользователя в проекте
        sql = 'SELECT role_project FROM project_members WHERE project_id = (%s) AND user_id = (%s)'
        row = self.db_helper.fetch_one(sql, (project_id, user_id))
        if not row:
            return None
        return row['role_project']
    
    def get_project_by_id(self, project_id): # Вывод информации о проекте по ID проекта
        sql = 'SELECT * FROM projects WHERE project_id = (%s)'
        row = self.db_helper.fetch_one(sql, (project_id,))
        return Project.from_dict_or_none(row)