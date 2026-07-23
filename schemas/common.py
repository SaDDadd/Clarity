# Общие схемы (пагинация, ответы с ошибками)
from enum import Enum
class TaskStatus(Enum):
    PENDING = 'pending', IN_PROGRESS = 'in_progress', COMPLETED = 'completed'

class ProjectRole(Enum):
    ADMIN = 'admin', MEMBER = 'member'