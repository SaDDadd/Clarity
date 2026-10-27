APP_NAMESPACE = 'clarity'
USER_PREFIX = f'{APP_NAMESPACE}:user'
PROJECT_PREFIX = f'{APP_NAMESPACE}:project'
TASK_PREFIX = f'{APP_NAMESPACE}:task'
INVITATION_PREFIX = f'{APP_NAMESPACE}:invitation'
RATE_LIMITING_PREFIX = f'{APP_NAMESPACE}:rate_limit'

TTL_USER_LIST = 180
TTL_USER = 300
TTL_PROJECT_LIST = 180
TTL_PROJECT = 120
TTL_TASK_LIST = 180
TTL_TASK = 120
TTL_INVITATION_LIST = 180
TTL_INVITATION = 120
TTL_TASK_COMMENT_LIST = 180
TTL_TASK_COMMENT = 120

def make_key(*parts) -> str:
    """Склеивает части ключа через ':', отбрасывая None."""
    return ':'.join(str(p) for p in parts if p is not None)

def user_key(user_id: int) -> str:
    """Ключ профиля пользователя. Используется в /profile."""
    return make_key(USER_PREFIX, user_id)

def project_key(project_id: int) -> str:
    """Ключ деталей проекта (включая участников)."""
    return make_key(PROJECT_PREFIX, project_id)

def task_key(project_id: int, task_id: int) -> str:
    """Ключ задачи."""
    return make_key(PROJECT_PREFIX, project_id, 'task', task_id)

def invitations_key(project_id: int, invitation_id: int) -> str:
    """Ключ одного приглашения внутри проекта."""
    return make_key(PROJECT_PREFIX, project_id, 'invitation', invitation_id)

def user_projects_key(user_id: int, kind: str = 'all') -> str:
    """Ключ списка проектов пользователя. kind: 'all' | 'admin'."""
    return make_key(USER_PREFIX, user_id, kind)

def user_tasks_key(user_id: int, task_id: int | str = 'all') -> str:
    """Ключ списка задач пользователя (task_id='all' — весь список)."""
    return make_key(USER_PREFIX, user_id, 'task', task_id)

def user_invitations_key(user_id: int, invitation_id: int | str = 'all') -> str:
    """Ключ списка входящих приглашений пользователя (invitation_id='all' - весь список)."""
    return make_key(USER_PREFIX, user_id, 'invitations', invitation_id)

def project_tasks_key(project_id: int) -> str:
    """Ключ списка задач проекта (task_id='all' — весь список)."""
    return make_key(PROJECT_PREFIX, project_id, 'task')

def project_invitations_key(project_id: int, invitation_id: int | str = 'all') -> str:
    """Ключ списка приглашений проекта (invitation_id='all' — весь список)."""
    return make_key(PROJECT_PREFIX, project_id, 'invitations', invitation_id)

def task_comment_key(project_id: int, task_id: int, comment_id: int) -> str:
    """Ключ комментария к задаче."""
    return make_key(PROJECT_PREFIX, project_id, 'task', task_id, 'comment', comment_id)

def task_comments_list_key(project_id: int, task_id: int) -> str:
    """Ключ списка комментариев задачи."""
    return make_key(PROJECT_PREFIX, project_id, 'task', task_id, 'comments')

def task_comments_pattern(project_id: int, task_id: int) -> str:
    """Паттерн: и элементы, и список комментариев задачи."""
    return make_key(PROJECT_PREFIX, project_id, 'task', task_id, 'comment*')

def project_comments_pattern(project_id: int) -> str:
    """Паттерн всех комментариев проекта."""
    return make_key(PROJECT_PREFIX, project_id, 'task', '*', 'comment*')

def project_invitations_pattern(project_id: int) -> str:
    """Паттерн всех приглашений проекта (список + одиночные)."""
    return make_key(PROJECT_PREFIX, project_id, 'invitations*')

def rate_limiting() -> str:
    """Базовый префикс для ключей rate limiting."""
    return make_key(RATE_LIMITING_PREFIX)

def user_cache_patterns(user_id: int) -> list[str]:
    """Паттерны для инвалидации всех ключей пользователя."""
    return [
        user_key(user_id),
        f'{USER_PREFIX}:{user_id}:*',
    ]

def project_cache_patterns(project_id: int) -> list[str]:
    """Паттерны для инвалидации всех ключей проекта."""
    return [
        project_key(project_id),
        f'{PROJECT_PREFIX}:{project_id}:*',
    ]