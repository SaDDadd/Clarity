class Project:
    def __init__(self, project_id: int, project_name: str, project_description: str,
                 admin_id: int) -> None: # Конструктор
        self._project_id = project_id
        self._project_name = project_name
        self._project_description = project_description
        self._admin_id = admin_id

    @classmethod 
    def from_dict(cls, data: dict) -> "Project": # Создать объект из словаря
        return cls(project_id = data.get('project_id'), project_name = data.get('project_name'),
                   project_description = data.get('project_description'), admin_id = data.get('admin_id'))

    @classmethod 
    def from_dict_or_none(cls, data: dict | None) -> "Project" | None: # Создать объект или вернуть None
        return cls.from_dict(data) if data else None

    def set_project_id(self, project_id: int) -> None: # Установить ID проекта
        self._project_id = project_id

    def set_project_name(self, project_name: str) -> None: # Установить название проекта
        self._project_name = project_name

    def set_project_description(self, project_description: str) -> None: # Установить описание проекта
        self._project_description = project_description

    def set_admin_id(self, admin_id: int) -> None: # Установить ID администратора
        self._admin_id = admin_id

    def get_project_id(self) -> int: # Получить ID проекта
        return self._project_id

    def get_project_name(self) -> str: # Получить название проекта
        return self._project_name

    def get_project_description(self) -> str: # Получить описание проекта
        return self._project_description

    def get_admin_id(self) -> int: # Получить ID администратора
        return self._admin_id

    def __str__(self) -> str: # Строковое представление
        return f'Проект id:{self._project_id}, название {self._project_name}, \
              описание проекта ({self._project_description}), админ:{self._admin_id}'