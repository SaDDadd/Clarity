# Общие схемы (пагинация, ответы с ошибками)
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

class ProjectRole(str, Enum):
    ADMIN = 'admin'
    MEMBER = 'member'