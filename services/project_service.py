# Создание, получение, обновление проектов, проверка прав
from repositories.project_repository import ProjectRepository
from schemas.project import ProjectCreate, ProjectsGet, ProjectUpdate, ProjectMember

async def create_project(db, project_date:ProjectCreate): # Создание проекта
    repo = ProjectRepository(db)
    try:
        repo.create_project_with_admin(project_date.project_name, project_date.project_description, project_date.admin_id)
    except:
        raise 

async def get_admin_projects(db, project_date:ProjectsGet): # Получить все проекты админа
    repo = ProjectRepository(db)
    if repo.get_projects_by_admin(project_date.admin_id) is None:
        raise
    else:
        numb_projects = len(repo.get_projects_by_admin(project_date.admin_id))
        return {item: numb_projects[item] for item in range(numb_projects)} 

async def update_project_all(db, project_date:ProjectUpdate):
    repo = ProjectRepository(db)
    if repo.update_project_description(project_date.project_description, project_date.project_id) is True:
        if repo.update_project_name(project_date.project_name, project_date.project_id) is True:
            return {}
        else:
            raise
    else:
        raise 

async def update_project_description(db, project_date:ProjectUpdate):
    repo = ProjectRepository(db)
    if repo.update_project_description(project_date.project_description, project_date.project_id) is True:
        return 
    else:
        raise 

async def update_project_name(db, project_date:ProjectUpdate):
    repo = ProjectRepository(db)
    if repo.update_project_name(project_date.project_name, project_date.project_id) is True:
        return {}
    else:
        raise

async def checking_rights_project(db, project_date:ProjectMember):
    repo = ProjectRepository(db)
    return repo.get_user_role_in_project(project_date.project_id, project_date.user_id)
    