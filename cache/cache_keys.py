APP_NAMESPACE = 'clarity'
USER_PREFIX = f'{APP_NAMESPACE}:user'
PROJECT_PREFIX = f'{APP_NAMESPACE}:project'
TASK_PREFIX = f'{APP_NAMESPACE}:task'
INVITATION_PREFIX = f'{APP_NAMESPACE}:invitation'
RATE_LIMITING_PREFIX = f'{APP_NAMESPACE}:rate_limit'

TTL_USER_LIST = 180
TTL_USER = 300
TTL_PROJECT = 120
TTL_TASK_LIST = 120
TTL_TASK = 180
TTL_INVITATION = 180

def make_key(*parts) -> str:
    """Склеивает части ключа через ':', отбрасывая None."""
    return ':'.join(str(p) for p in parts if p is not None)

def user_key(user_id: int) -> str:
    """Ключ профиля пользователя. Используется в /profile и /auth/me."""
    return make_key(USER_PREFIX, user_id)

def project_key(project_id: int) -> str:
    """Ключ деталей проекта (включая участников)."""
    return make_key(PROJECT_PREFIX, project_id)

def task_key(project_id: int, task_id: int) -> str:
    """Ключ задачи. Задача всегда живёт внутри проекта — project_id в пути."""
    return make_key(PROJECT_PREFIX, project_id, 'task', task_id)

def invitations_key(project_id: int, invitation_id: int) -> str:
    """Ключ приглашений."""
    return make_key(PROJECT_PREFIX, project_id, 'invitation', invitation_id)

def user_projects_key(user_id: int, kind: str = 'all') -> str:
    """"""
    return make_key(USER_PREFIX, user_id, kind)

def user_tasks_key(user_id: int, task_id: int = 'all') -> str:
    """"""
    return make_key(USER_PREFIX, user_id, 'task', task_id)

def user_invitations_key(user_id: int, invitation_id: int = 'all') -> str:
    """"""
    return make_key(USER_PREFIX, user_id, 'invitations', invitation_id)

def project_tasks_key(project_id: int, task_id: int = 'all'):
    """"""
    return make_key(PROJECT_PREFIX, project_id, 'task', task_id)

def project_invitations_key(project_id: int, invitation_id: int = 'all') -> str:
    """"""
    return make_key(PROJECT_PREFIX, project_id, 'invitations', invitation_id)

def rate_limiting() -> str:
    return make_key(RATE_LIMITING_PREFIX)

def user_cache_patterns():
    return []

def project_cache_patterns():
    return []