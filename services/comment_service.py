from core.uow import UnitOfWork
from core.exceptions import NotFoundException, PermissionDeniedException, ConflictException, \
                            LackOfInformationException
from cache.cache_keys import task_comments_list_key
from cache.cache_service import delete_cache
from core.filters import CommentFilter
from fastapi_pagination import Params, Page
from schemas.comment import TaskCommentResponse


async def update_comment(uow: UnitOfWork, project_id: int, task_id: int, comment_id: int,
                        message: str, current_user_id: int) -> dict:
    """Обновить комментарий."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    comment = await uow.comment.get_comment_by_id(comment_id)
    if comment is None:
        raise NotFoundException('Комментарий не найден!')
    if comment.project_id != project_id or comment.task_id != task_id:
        raise ConflictException('Данные не подходят!')
    is_admin_or_curator = await uow.project.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_admin_or_curator or comment.author_id == current_user_id):
        raise PermissionDeniedException('Только админ, куратор или автор комментария могут изменить комментарий!')
    if len(message) > 1000:
        raise LackOfInformationException('Длина комментария не может быть больше 1000 символов!')
    if message == comment.comment_text:
        return {'message': 'Комментарий не изменился!'}
    await uow.comment.update_comment(comment_id, message)
    await delete_cache(task_comments_list_key(project_id, task_id))
    return {'message': 'Комментарий обновлен!'}


async def get_task_comments(uow: UnitOfWork, project_id: int, task_id: int, current_user_id: int,
                                comment_filter: CommentFilter | None = None, params: Params | None = None) -> Page[dict]:
    """Список комментариев задачи."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    result = await uow.comment.get_task_comments(project_id, task_id, comment_filter, params)
    items = [TaskCommentResponse.model_validate(comment).model_dump(mode='json') for comment in result.items]
    return Page[TaskCommentResponse](
        items=items,
        total=result.total,
        page=result.page,
        size=result.size,
        pages=result.pages
    )


async def create_task_comment(uow: UnitOfWork, project_id: int, task_id: int,
                              message: str, current_user_id: int) -> dict:
    """Создаёт комментарий."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    result = await uow.comment.create_comment(project_id, task_id, current_user_id, message)
    await uow.session.refresh(result)
    await delete_cache(task_comments_list_key(project_id, task_id))
    return result


async def delete_task_comment(uow: UnitOfWork, project_id: int, task_id: int, comment_id: int,
                              current_user_id: int) -> dict:
    """Удалить комментарий у задачи."""
    if await uow.project.get_project_by_id(project_id) is None:
        raise NotFoundException('Данного проекта не существует!')
    if not await uow.project.is_user_in_project(project_id, current_user_id):
        raise PermissionDeniedException('Текущего пользователя нет в проекте!')
    if not await uow.task.is_task_in_project(project_id, task_id):
        raise NotFoundException('Задачи нет в проекте!')
    comment_info = await uow.comment.get_comment_by_id(comment_id)
    if comment_info is None:
        raise NotFoundException('Комментарий не найден!')
    if comment_info.project_id != project_id or comment_info.task_id != task_id:
        raise ConflictException('Данные не подходят!')
    author_id = comment_info.author_id
    is_admin_or_curator = await uow.project.is_user_admin_or_curator(project_id, current_user_id)
    if not (is_admin_or_curator or (author_id is not None and author_id == current_user_id)):
        raise PermissionDeniedException('Не админ и не создатель комментария не может его удалить!')
    await uow.comment.delete_comment(comment_id)
    await delete_cache(task_comments_list_key(project_id, task_id))
    return {'message': 'Комментарий удален!'}