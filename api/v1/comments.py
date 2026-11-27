from fastapi import APIRouter, Depends
from schemas.comment import TaskCommentCreate, TaskCommentResponse
from core.filters import CommentFilter
from models.user import UserModel
from core.uow import UnitOfWork
from core.dependencies import get_uow, current_user
from services.comment_service import update_comment, get_task_comments, create_task_comment, delete_task_comment
from fastapi_pagination import Page, Params
from fastapi_filter import FilterDepends


router = APIRouter()


@router.put('/projects/{project_id}/tasks/{task_id}/comments/{comment_id}', response_model=dict, tags=['Комментарии'],
            summary='Обновление комментария задачи.')
async def update_comment_endpoint(message: TaskCommentCreate, project_id: int, task_id: int,
                                  comment_id: int, current_user: UserModel = Depends(current_user),
                                  uow: UnitOfWork = Depends(get_uow)):
    """Обновление комментария."""
    return await update_comment(uow, project_id, task_id, comment_id, message.comment_text, current_user.user_id)


@router.get('/projects/{project_id}/tasks/{task_id}/comments', response_model=Page[TaskCommentResponse], tags=['Комментарии'],
            summary='Получить комментарии задачи')
async def get_task_comments_endpoint(project_id: int, task_id: int,
                                     current_user: UserModel = Depends(current_user),
                                     comment_filter: CommentFilter = FilterDepends(CommentFilter),
                                     params: Params = Depends(),
                                     uow: UnitOfWork = Depends(get_uow)):
    """Возвращает комментарии задачи."""
    # добавить фильтраию и пагинацию
    return await get_task_comments(uow, project_id, task_id, current_user.user_id, comment_filter, params)


@router.post('/projects/{project_id}/tasks/{task_id}/comments', response_model=TaskCommentResponse, tags=['Комментарии'],
             summary='Написать комментарий к задаче.')
async def create_task_comment_endpoint(message: TaskCommentCreate, project_id: int, task_id: int,
                                       current_user: UserModel = Depends(current_user),
                                       uow: UnitOfWork = Depends(get_uow)):
    """Написать комментарий к задаче проекта."""
    return await create_task_comment(uow, project_id, task_id, message.comment_text, current_user.user_id)


@router.delete('/projects/{project_id}/tasks/{task_id}/comments/{comment_id}', response_model=dict, tags=['Комментарии'],
               summary='Удалить комментарий к задаче.')
async def delete_task_comment_endpoint(project_id: int, task_id: int, comment_id: int,
                                      current_user: UserModel = Depends(current_user),
                                      uow: UnitOfWork = Depends(get_uow)):
    """Удаление комментария задачи."""
    return await delete_task_comment(uow, project_id, task_id, comment_id, current_user.user_id)