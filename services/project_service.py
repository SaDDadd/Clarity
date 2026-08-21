# Создание, получение, обновление проектов, проверка прав
from core.exceptions import AppException, NotFoundException, PermissionDeniedException,\
            ConflictException, LastAdminDeletionException, InvalidInvitationStateException
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from schemas.project import ProjectCreate, ProjectMemberCheck, ProjectUpdate

# Создание проекта
async def create_project(db, project_date: ProjectCreate, admin_id):
    repo = ProjectRepository(db)
    return await repo.create_project_with_admin(
        project_date.project_name,
        project_date.project_description,
        admin_id,
        role='admin'
    )

# Добавить пользователя в проект
async def add_user(db, project_id: int, current_user_id: int, user_id_to_add: int):
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя добавить пользователя: вы не админ проекта!')
    if current_user_id == user_id_to_add:
        raise InvalidInvitationStateException('Нельзя добавить самого себя!')
    if not await repo_user.check_user_exists(user_id_to_add):
        raise NotFoundException('Нельзя добавить пользователя: его не существует!')
    if await repo.is_user_in_project(project_id, user_id_to_add):
        raise ConflictException('Пользователь уже состоит в проекте')
    if await repo.add_user(project_id, user_id_to_add):
        return {'message': 'Пользователь добавлен в проект!'}
    raise AppException(500, 'Неизвестная ошибка при добавлении пользователя в проект!')

# Получить все проекты админа
async def get_admin_projects(db, admin_id: int):
    repo = ProjectRepository(db)
    numb_projects = await repo.get_projects_by_admin(admin_id)
    if not numb_projects:
        return []
    else:
        return numb_projects

# Проверка прав пользователя в проекте
async def checking_rights_project(db, project_date: ProjectMemberCheck):
    repo = ProjectRepository(db)
    result = await repo.get_user_role_in_project(project_date.project_id, project_date.user_id)
    if result is None:
        raise PermissionDeniedException('Пользователь не состоит в проекте!')
    else:
        return result

# Получить информацию о проекте
async def get_project_info(db, project_id: int, user_id: int):
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_in_project(project_id, user_id):
        raise PermissionDeniedException('Пользователь не является участником проекта!')
    return await repo.get_project_all_info(project_id)

# Получить все проекты пользователя
async def get_user_projects(db, current_user_id: int):
    repo = ProjectRepository(db)
    projects = await repo.get_user_projects(current_user_id)
    result = []
    for project in projects:
        role = await repo.get_user_role_in_project(project.project_id, current_user_id)
        result.append({
            'project_id': project.project_id,
            'project_name': project.project_name,
            'project_description': project.project_description,
            'role': role
        })
    return result

# Обновить проект
async def update_project(db, project_id: int, user_id: int, project_date: ProjectUpdate):
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

# Удалить проект
async def delete_project(db, project_id: int, user_id: int):
    repo = ProjectRepository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise NotFoundException('Проект не найден!')
    if not await repo.is_user_admin(project_id, user_id):
        raise PermissionDeniedException('Вы не админ этого проекта!')
    if await repo.delete_project(project_id):
        return {'message': 'Проект успешно удален!'}
    raise AppException(500, 'Не удалось удалить проект')

# Удалить пользователя из проекта
async def delete_project_user(db, project_id: int, current_user_id: int, user_id_to_del: int):
    repo = ProjectRepository(db)
    repo_user = UserRepository(db)
    if not await repo_user.check_user_exists(user_id_to_del):
        raise NotFoundException('Нельзя удалить пользователя: его не существует!')
    if not await repo.is_user_admin(project_id, current_user_id):
        raise PermissionDeniedException('Нельзя удалить пользователя: вы не админ проекта!')
    if not await repo.is_user_in_project(project_id, user_id_to_del):
        raise ConflictException('Пользователь не состоит в проекте!')
    if await repo.is_user_admin(project_id, user_id_to_del):
        admins_count = await repo.get_number_admins(project_id)
        if admins_count == 1:
            raise LastAdminDeletionException('Нельзя удалить единственного администратора проекта!')
        project = await repo.get_project_by_id(project_id)
        if project.admin_id == user_id_to_del:
            admins = await repo.get_admins_list(project_id)
            other_admin = next((a for a in admins if a.user_id != user_id_to_del), None)
            if other_admin:
                await repo.reassign_admin(project_id, other_admin.user_id)
            else:
                raise AppException(500, 'Не удалось переназначить администратора')
    deleted = await repo.delete_user(project_id, user_id_to_del)
    if not deleted:
        raise AppException(500, 'Неизвестная ошибка при удалении пользователя из проекта!')
    return {'message': 'Пользователь удален из проекта!'}