# Создание, получение, обновление проектов, проверка прав
from repositories.project_repository import ProjectRepository
from schemas.project import ProjectBase, ProjectsGet, ProjectUpdate, ProjectMember, PermissionDeniedException
from core.exceptions import NotFoundException, PermissionDeniedException

async def create_project(db, project_date:ProjectBase): # Создание проекта
    repo = ProjectRepository(db)
    return await repo.create_project_with_admin(project_date.project_name, project_date.project_description, project_date.admin_id, 'admin')


async def get_admin_projects(db, project_date:ProjectsGet): # Получить все проекты админа
    repo = ProjectRepository(db)
    numb_projects = await repo.get_projects_by_admin(project_date.admin_id)
    if numb_projects is None:
        return {'message': 'У пользователя нет проектов!'}
    else:
        return numb_projects

async def update_project(db, project_date:ProjectUpdate):
    repo = ProjectRepository(db)
    result = await repo.get_project_by_id(project_date.project_id)
    if result:
        if await repo.get_user_role_in_project(project_date.user_id, project_date.project_id) == 'admin':
            await repo.update_project()
            return {'message':}
        else:
            raise PermissiondeniedException('Пользователь не может менять проект, он не админ!')
    else:
        raise NotFoundException('Проект не найден!')
    

async def checking_rights_project(db, project_date:ProjectMember):
    repo = ProjectRepository(db)
    result = await repo.get_user_role_in_project(project_date.project_id, project_date.user_id)
    if result is None:
        raise PermissionDeniedException('Пользователь не состоит в проекте!')
    else:
        return result
    