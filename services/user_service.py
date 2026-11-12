from core.exceptions import ConflictException, LackOfInformationException, NotFoundException
from core.uow import UnitOfWork
from schemas.user import (UserResponse, UpdateUsernameRequest, UpdateEmailRequest, 
                          UpdatePasswordRequest, UserSearchResponse)
from models.user import UserModel
from core.security import async_hash_password
from cache.cache_keys import (user_key, user_all_pattern, user_projects_pattern,
                                user_invitations_pattern, project_all_pattern, project_key, TTL_USER,
                                user_tasks_pattern, project_invitations_key, task_comments_list_key
                            )
from cache.cache_service import (set_cache, get_cache, delete_cache, delete_cache_by_pattern)


async def update_user_username(uow: UnitOfWork, user_data: UpdateUsernameRequest, current_user_id: int) -> dict:
    """Изменить имя пользователя."""
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data or update_data.get('username') is None:
        raise LackOfInformationException('Не указано новое имя пользователя!')
    username = update_data['username'].strip()
    if len(username) == 0 or len(username) > 50:
        raise LackOfInformationException('Имя не может быть пустым или превышать 50 символов!')
    if await uow.user.check_user_exists_by_username_excluding_current(username, current_user_id):
        raise ConflictException('Пользователь с таким именем уже существует!')
    await uow.user.update_username(current_user_id, username)
    await delete_cache(user_key(current_user_id))
    incoming = await uow.invitation.get_invitation_by_user(current_user_id)
    for inv in incoming:
        await delete_cache(project_invitations_key(inv.project_id, 'all'))
    return {'message': 'Имя пользователя обновлено!'}


async def update_user_email(uow: UnitOfWork, user_data: UpdateEmailRequest, current_user_id: int) -> dict:
    """Изменить email пользователя."""
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data or update_data.get('email') is None:
        raise LackOfInformationException('Не указан новый email!')
    email = str(update_data['email'])
    if len(email) == 0 or len(email) > 100:
        raise LackOfInformationException('Email не может быть пустым или превышать 100 символов!')
    if await uow.user.check_user_exists_by_email_excluding_current(email, current_user_id):
        raise ConflictException('Пользователь с таким email уже существует!')
    await uow.user.update_email(current_user_id, email)
    await delete_cache(user_key(current_user_id))
    return {'message': 'Email пользователя обновлено!'}


async def update_user_password(uow: UnitOfWork, user_data: UpdatePasswordRequest, current_user_id: int) -> dict:
    """Изменить пароль пользователя."""
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data or update_data.get('password') is None:
        raise LackOfInformationException('Не указан новый пароль!')
    password = update_data['password']
    if len(password) < 8 or len(password) > 50:
        raise LackOfInformationException('Пароль должен быть от 8 до 50 символов!')
    hashed_password = await async_hash_password(password)
    await uow.user.update_password(current_user_id, hashed_password)
    await delete_cache(user_key(current_user_id))
    return {'message': 'Пароль пользователя обновлен!'}


async def search_by_username(uow: UnitOfWork, search_user: str, current_user_username: str) -> list[UserSearchResponse]:
    """Поиск пользователя по имени."""
    if len(search_user) == 0:
        raise NotFoundException('Нельзя найти пользователя, введите ник!')
    if search_user == current_user_username:
        raise ConflictException('Нельзя искать самого себя!')
    user = await uow.user.search_by_username(search_user)
    if user:
        return user
    raise NotFoundException('Пользователь не найден!')


async def delete_profile(uow: UnitOfWork, current_user_id: int) -> dict:
    """Удаление профиля."""
    user = await uow.user.get_by_id(current_user_id)
    if user is None:
        raise NotFoundException('Пользователь не найден!')
    admin_projects = await uow.project.get_projects_by_creator(current_user_id)
    member_projects = await uow.project.get_user_projects(current_user_id)
    project_members_map: dict[int, list[int]] = {}
    project_ids: set[int] = set()
    affected_invitee_ids: set[int] = set()
    for project in member_projects:
        project_ids.add(project.project_id)
        info = await uow.project.get_project_all_info(project.project_id)
        project_members_map[project.project_id] = [
            m.user_id for m in info['members'] if m.user_id != current_user_id
        ]
    for pid in project_ids:
        pending = await uow.invitation.get_invitation_for_project(pid)
        affected_invitee_ids.update(inv.invitee_id for inv, _ in pending)
    invited_project_ids: set[int] = set()
    incoming = await uow.invitation.get_invitation_by_user(current_user_id)
    for inv in incoming:
        if inv.project_id not in project_ids:
            invited_project_ids.add(inv.project_id)
    sent_invitations = await uow.invitation.get_pending_invitations_by_inviter(current_user_id)
    sent_project_ids = {inv.project_id for inv in sent_invitations}
    sent_invitee_ids = {inv.invitee_id for inv in sent_invitations}
    project_invitation_ids = sent_project_ids | invited_project_ids
    invitee_ids_to_invalidate = affected_invitee_ids | sent_invitee_ids
    comment_locations = await uow.task.get_task_comment_locations_by_author(current_user_id)
    await uow.project.unassign_all_tasks_from_user(current_user_id)
    for project in admin_projects:
        new_owner_id = await uow.project.automatically_assign_admin(project.project_id, current_user_id)
        if new_owner_id is None:
            await uow.project.delete_project(project.project_id)
    await uow.user.delete_user(current_user_id)
    for pid in project_ids:
        await delete_cache(project_key(pid))
        await delete_cache_by_pattern(project_all_pattern(pid))
    for members in project_members_map.values():
        for mid in members:
            await delete_cache_by_pattern(user_projects_pattern(mid))
            await delete_cache_by_pattern(user_tasks_pattern(mid))
    for iid in invitee_ids_to_invalidate:
        await delete_cache_by_pattern(user_invitations_pattern(iid))
    for pid in project_invitation_ids:
        await delete_cache(project_invitations_key(pid, 'all'))
    for pid, tid in comment_locations:
        await delete_cache(task_comments_list_key(pid, tid))
    await delete_cache(user_key(current_user_id))
    await delete_cache_by_pattern(user_all_pattern(current_user_id))
    return {'message': 'Профиль удален!'}


async def get_profile_info(current_user: UserModel) -> dict:
    """Возвращает данные текущего пользователя."""
    key = user_key(current_user.user_id)
    cached = await get_cache(key)
    if cached is not None:
        return cached
    data = UserResponse.model_validate(current_user).model_dump(mode='json')
    await set_cache(key, data, TTL_USER)
    return data