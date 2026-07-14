import pymysql 
from db.connection_manager import DatabaseHelper
from models.project import Project

class ProjectRepository:
    def __init__(self):
        self.db_helper = DatabaseHelper()

    def create_project(self, name, description, ad_id): # Создание нового проекта
        sql = 'INSERT INTO projects (project_name, project_description, \
            admin_id)' \
        'VALUES (%s, %s, %s)'

        return self.db_helper.execute_query(sql, (name, description, ad_id))

    def get_projects_by_admin(self, admin_id): # Вывод все проектов прикрепленных к администратору
        sql = 'SELECT * FROM projects WHERE admin_id = (%s)'
        row = self.db_helper.fetch_all(sql, (admin_id,))
        return [Project.from_dict(item) for item in row]

    def update_project_description(self, new_description, project_id): # Обновление описания проекта
        sql = 'UPDATE projects SET project_description = (%s) WHERE project_id = (%s)'

        return self.db_helper.execute_query(sql, (new_description, project_id))

    def check_project_exists(self, project_id): # Проверка существования проекта
        sql = 'SELECT project_id FROM projects WHERE project_id = (%s)'

        return self.db_helper.fetch_one(sql, (project_id,))