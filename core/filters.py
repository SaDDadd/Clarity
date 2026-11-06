from fastapi_filter import Filter
from models.user import UserModel
from models.project import ProjectModel
from models.task import TaskModel
from models.project_invitations import ProjectInvitationModel 
from models.task_comments import TaskCommentsModel
from sqlalchemy import Enum
import datetime


class UserFilter(Filter):
    """Фильтрация работы с пользователями."""
    username: str
    class Constants(Filter.Constants):
        model = UserModel


class ProjectFilter(Filter):
    """Фильтрация работы с проектами."""
    project_name: str
    created_date: datetime.datetime
    class Constants(Filter.Constants):
        model = ProjectModel


class TaskFilter(Filter):
    """Фильтрация работы с задачами."""
    title: str 
    task_status: Enum
    task_priority: Enum
    task_favorite: bool | None = None
    deadline: datetime.datetime | None = None
    created_date: datetime.datetime | None = None
    class Constants(Filter.Constants):
        model = TaskModel


class InvitationFilter(Filter):
    """Фильтрация работы с приглашениями."""
    inviter_id: int
    invitee_id: int 
    status_invited: Enum
    created_date: datetime.datetime
    class Constants(Filter.Constants):
        model = ProjectInvitationModel


class CommentFilter(Filter):
    """Фильтрация работы с комментариями."""
    author_id: int | None = None
    created_date: datetime.datetime
    class constants(filter.Constants):
        model = TaskCommentsModel