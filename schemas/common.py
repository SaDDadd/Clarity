from enum import Enum

class TaskStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

class ProjectRole(str, Enum):
    ADMIN = 'admin'
    CURATOR = 'curator'
    MEMBER = 'member'

class InvitationRole(str, Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'

class InvitationAction(str, Enum):
    ACCEPTED = 'accepted'
    DECLINED = 'declined'

class TaskPriority(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'