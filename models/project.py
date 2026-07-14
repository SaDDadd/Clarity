class Project:
    def __init__(self, project_id, project_name, project_description, \
                 admin_id):
        self._project_id = project_id
        self._project_name = project_name
        self._project_description = project_description
        self._admin_id = admin_id

    @classmethod 
    def from_dict(cls, data: dict): # Разбиение словаря после запроса
        return cls(project_id = data.get('project_id'), project_name = data.get('project_name'), \
                   project_description = data.get('project_description'), admin_id = data.get('admin_id'))

    @classmethod 
    def from_dict_or_none(cls, data): # Проверка, если в запросе выводиться None
        return cls.from_dict(data) if data else None

    def set_project_id(self, project_id):
        self._project_id = project_id

    def set_project_name(self, project_name):
        self._project_name = project_name

    def set_project_description(self, project_description):
        self._project_description = project_description

    def set_admin_id(self, admin_id):
        self._admin_id = admin_id

    def get_project_id(self):
        return self._project_id

    def get_project_name(self):
        return self._project_name

    def get_project_description(self):
        return self._project_description

    def get_admin_id(self):
        return self._admin_id

    def __str__(self):
        return f'Проект id:{self._project_id}, название {self._project_name}, \
              описание проекта ({self._project_description}), админ:{self._admin_id}'