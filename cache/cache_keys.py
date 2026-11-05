APP_NAMESPACE = 'clarity'
USER_PREFIX = f'{APP_NAMESPACE}:user'
PROJECT_PREFIX = f'{APP_NAMESPACE}:project'
RATE_LIMITING_PREFIX = f'{APP_NAMESPACE}:rate_limit'

TTL_USER = 300
TTL_PROJECT = 120
TTL_PROJECT_LIST = 180
TTL_TASK = 120
TTL_TASK_LIST = 180
TTL_INVITATION_LIST = 180
TTL_TASK_COMMENT_LIST = 180


def make_key(*parts) -> str:
    """Склеивает части ключа."""
    return ':'.join(str(p) for p in parts if p is not None)

def user_key(user_id: int) -> str:
    """Профиль: clarity:user:{id}"""
    return make_key(USER_PREFIX, user_id)

def user_projects_key(user_id: int, kind: str | None = None) -> str:
    """Проекты пользователя. kind: all/admin."""
    return make_key(USER_PREFIX, user_id, 'projects', kind)


def user_tasks_key(user_id: int, kind: str | None = None) -> str:
    """Задачи пользователя. kind: all."""
    return make_key(USER_PREFIX, user_id, 'tasks', kind)


def user_invitations_key(user_id: int, kind: str | None = None) -> str:
    """Приглашения пользователя. kind: all."""
    return make_key(USER_PREFIX, user_id, 'invitations', kind)

def user_projects_pattern(user_id: int) -> str:
    """Все ключи проектов пользователя: base + all/admin."""
    return make_key(USER_PREFIX, user_id, 'projects*')

def user_tasks_pattern(user_id: int) -> str:
    """Все ключи задач пользователя: base + all."""
    return make_key(USER_PREFIX, user_id, 'tasks*')

def user_invitations_pattern(user_id: int) -> str:
    """Все ключи приглашений пользователя: base + all."""
    return make_key(USER_PREFIX, user_id, 'invitations*')

def user_all_pattern(user_id: int) -> str:
    """Все дочерние ключи пользователя."""
    return make_key(USER_PREFIX, user_id, '*')

def user_cache_patterns(user_id: int) -> list[str]:
    """Все паттерны пользователя для каскадной инвалидации."""
    return [user_all_pattern(user_id)]

def project_key(project_id: int) -> str:
    """Детали проекта + участники."""
    return make_key(PROJECT_PREFIX, project_id)

def project_tasks_key(project_id: int) -> str:
    """Список задач проекта."""
    return make_key(PROJECT_PREFIX, project_id, 'tasks')

def project_task_items_pattern(project_id: int) -> str:
    """Детали задач и комментарии проекта, но не список tasks."""
    return make_key(PROJECT_PREFIX, project_id, 'task', '*')

def project_invitations_key(project_id: int, kind: str | None = None) -> str:
    """Список приглашений проекта. kind: all."""
    return make_key(PROJECT_PREFIX, project_id, 'invitations', kind)

def project_invitations_pattern(project_id: int) -> str:
    """Все ключи приглашений проекта."""
    return make_key(PROJECT_PREFIX, project_id, 'invitations*')

def project_all_pattern(project_id: int) -> str:
    """Каскад: все дочерние ключи проекта."""
    return make_key(PROJECT_PREFIX, project_id, '*')

def task_key(project_id: int, task_id: int) -> str:
    """Детали задачи."""
    return make_key(PROJECT_PREFIX, project_id, 'task', task_id)

def task_comments_list_key(project_id: int, task_id: int) -> str:
    """Комментарии задачи."""
    return make_key(PROJECT_PREFIX, project_id, 'task', task_id, 'comments')

def task_comments_pattern(project_id: int, task_id: int) -> str:
    """Сам ключ задачи + комментарии."""
    return make_key(PROJECT_PREFIX, project_id, 'task', task_id) + '*'

def project_comments_pattern(project_id: int) -> str:
    """Все комментарии всех задач проекта."""
    return make_key(PROJECT_PREFIX, project_id, 'task', '*', 'comments')

def rate_limiting() -> str:
    return make_key(RATE_LIMITING_PREFIX)