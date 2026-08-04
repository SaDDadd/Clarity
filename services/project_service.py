# Создание, получение, обновление проектов, проверка прав
from repositories.project_repository import ProjectRepository
from schemas.project import ProjectUpdate, ProjectMemberCheck, ProjectCreate, ProjectResponse
from core.exceptions import NotFoundException, PermissionDeniedException

async def create_project(db, project_date:ProjectCreate, admin_id): # Создание проекта
    repo = ProjectRepository(db)
    return await repo.create_project_with_admin(project_date.project_name, project_date.project_description, admin_id, role='admin')
    # В будущем можно добавить проверку на уникальность имени проекта у одного админа

async def get_admin_projects(db, admin_id: int): # Получить все проекты админа
    repo = ProjectRepository(db)
    numb_projects = await repo.get_projects_by_admin(admin_id)
    if not numb_projects:
        return []
    else:
        return numb_projects

async def update_project(db, project_id: int, user_id: int, project_date:ProjectUpdate):
    repo = ProjectRepository(db)
    result = await repo.get_project_by_id(project_id)
    if result:
        if await repo.get_user_role_in_project(project_id, user_id) == 'admin':
            if project_date.project_description is None and project_date.project_name is None:
                return {'message': 'Ничего не изменилось!'}
            if project_date.project_description is None:
                await repo.update_project_name(project_date.project_name, project_id)
            elif project_date.project_name is None:
                await repo.update_project_description(project_date.project_description, project_id)
            else:
                await repo.update_project_description(project_date.project_description, project_id)
                await repo.update_project_name(project_date.project_name, project_id)
            return {'message': 'Проект обновлен!'}
        else:
            raise PermissionDeniedException('Пользователь не может менять проект, он не админ!')
    else:
        raise NotFoundException('Проект не найден!')
    

async def checking_rights_project(db, project_date:ProjectMemberCheck):
    repo = ProjectRepository(db)
    result = await repo.get_user_role_in_project(project_date.project_id, project_date.user_id)
    if result is None:
        raise PermissionDeniedException('Пользователь не состоит в проекте!')
    else:
        return result

async def get_project_info(db, project_id: int, user_id: int):
    repo = ProjectRepository(db)
    if await repo.is_user_in_project(project_id, user_id):
        return await repo.get_project_all_info(project_id)
    else:
        raise PermissionDeniedException('Пользователь не является участником проекта!')
