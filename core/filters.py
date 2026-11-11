from fastapi_filter.contrib.sqlalchemy import Filter
from models.user import UserModel
from models.project import ProjectModel
from models.task import TaskModel
from models.project_invitations import ProjectInvitationModel 
from models.task_comments import TaskCommentsModel
from schemas.common import TaskStatus, TaskPriority, InvitationRole
import datetime


class UserFilter(Filter):
    """Фильтрация работы с пользователями."""
    username: str | None = None
    class Constants(Filter.Constants):
        model = UserModel


class ProjectFilter(Filter):
    """Фильтрация работы с проектами."""
    project_name: str | None = None
    created_date: datetime.datetime | None = None
    class Constants(Filter.Constants):
        model = ProjectModel


class TaskFilter(Filter):
    """Фильтрация работы с задачами."""
    title: str | None = None
    task_status: TaskStatus | None = None
    task_priority: TaskPriority | None = None
    task_favorite: bool | None = None
    deadline: datetime.date | None = None
    created_date: datetime.datetime | None = None
    class Constants(Filter.Constants):
        model = TaskModel


class InvitationFilter(Filter):
    """Фильтрация работы с приглашениями."""
    inviter_id: int | None = None
    invitee_id: int | None = None
    status_invited: InvitationRole | None = None
    created_date: datetime.datetime | None = None
    class Constants(Filter.Constants):
        model = ProjectInvitationModel


class CommentFilter(Filter):
    """Фильтрация работы с комментариями."""
    author_id: int | None = None
    created_date: datetime.datetime | None = None
    class Constants(Filter.Constants):
        model = TaskCommentsModel