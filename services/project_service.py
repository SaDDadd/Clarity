# Создание, получение, обновление проектов, проверка прав
from repositories.project_repository import ProjectRepository
from schemas.project import ProjectBase, ProjectsGet, ProjectUpdate, ProjectMember

async def create_project(db, project_date:ProjectBase): # Создание проекта
    repo = ProjectRepository(db)
    try:
        repo.create_project_with_admin(project_date.project_name, project_date.project_description, project_date.admin_id)
    except:
        raise 

async def get_admin_projects(db, project_date:ProjectsGet): # Получить все проекты админа
    repo = ProjectRepository(db)
    numb_projects = repo.get_projects_by_admin(project_date.admin_id)
    if numb_projects is None:
        raise
    else:
        return numb_projects

async def update_project(db, project_date:ProjectUpdate):
    repo = ProjectRepository(db)
    

async def checking_rights_project(db, project_date:ProjectMember):
    repo = ProjectRepository(db)
    result = repo.get_user_role_in_project(project_date.project_id, project_date.user_id)
    if result is None:
        return {'message': 'Пользователя нет в проекте!'}
    