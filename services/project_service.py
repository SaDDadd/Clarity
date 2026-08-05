# Создание, получение, обновление проектов, проверка прав
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from schemas.project import ProjectUpdate, ProjectMemberCheck, ProjectCreate
from core.exceptions import NotFoundException, PermissionDeniedException, AppException

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

async def delete_project(db, project_id: int, user_id: int):
    repo = ProjectRepository(db)
    if await repo.is_user_admin(project_id, user_id):
        if await repo.delete_project(project_id):
            return {'message': 'Проект успешно удален!'}
        else:
            raise NotFoundException('Проект не найден!')
    else:
        raise PermissionDeniedException('Вы не админ этого проекта!')

async def add_user(db, project_id: int, current_user_id: int, user_id_to_add: int):
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    if await repo_user.check_user_exists(user_id_to_add) is False:
        raise NotFoundException('Нельзя добавить пользователя: его не существует!')
    if not await repo.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя добавить пользователя: вы не админ проекта!')
    else:
        result = await repo.add_user(project_id, user_id_to_add)
        if result:
            return {'message': 'Пользователь добавлен в проект!'}
        else:
            raise AppException('Неизвестная ошибка при добавлении пользователя в проект!')

async def delete_project_user(db, project_id: int, current_user_id: int, user_id_to_del: int):
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    if await repo_user.check_user_exists(user_id_to_del) is False:
        raise NotFoundException('Нельзя удалить пользователя: его не существует!')
    if not await repo.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя удалить пользователя: вы не админ проекта!')
    else:
        result = await repo.delete_user(project_id, user_id_to_del)
        if result:
            return {'message': 'Пользователь удален из проекта!'}
        else:
            raise AppException('Неизвестная ошибка при удалении пользователя из проекта!')
