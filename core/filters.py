from fastapi import Filter
from models.user import UserModel
from models.project import ProjectModel
from models.task import TaskModel
from models.project_invitations import ProjectInvitationModel 
from models.task_comments import TaskCommentsModel


class UserFilter(Filter):
    # поля для фильтрации
    """Фильтрация работы с пользователями."""
    class Constants(Filter.Constants):
        model = UserModel


class ProjectFilter(Filter):
    # поля для фильтрации
    """Фильтрация работы с проектами."""
    class Constants(Filter.Constants):
        model = ProjectModel


class TaskFilter(Filter):
    # поля для фильтрации
    """Фильтрация работы с задачами."""
    class Constants(Filter.Constants):
        model = TaskModel


class InvitationFilter(Filter):
    # поля для фильтрации
    """Фильтрация работы с приглашениями."""
    class Constants(Filter.Constants):
        model = ProjectInvitationModel


class CommentFilter(Filter):
    # поля для фильтрации
    """Фильтрация работы с комментариями."""
    class constants(filter.Constants):
        model = TaskCommentsModel