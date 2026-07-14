import datetime 

class Task:
    def __init__(self, task_id, title, task_description, task_status, \
                 project_id, assigned_to, deadline, created_date):
        self._task_id = task_id
        self._title = title 
        self._task_description = task_description
        self._task_status = task_status
        self._project_id = project_id
        self._assigned_to = assigned_to
        self._deadline = deadline
        self._created_date = created_date

    @classmethod
    def from_dict(cls, data: dict): # Разбиение словаря после запроса
        return cls(task_id = data.get('task_id'), title = data.get('title'), \
                   task_description = data.get('task_description'), task_status = data.get('task_status'), \
                    project_id = data.get('project_id'), assigned_to = data.get('assigned_to'), \
                        deadline = data.get('deadline'), created_date = data.get('created_date'))

    @classmethod
    def from_dict_or_none(cls, data): # Проверка, если в запросе выводиться None
        return cls.from_dict(data) if data else None
    
    def overdue(self, ): # Проверка на просроченную задачу
        if self._deadline < datetime.date.today():
            return f'Время deadline прошло {datetime.date.today() - self._deadline}'
        else:
            return f'Время до deadline {self._deadline - datetime.date.today()}'
        
    def set_task_id(self, task_id):
        self._task_id = task_id

    def set_title(self, title):
        self._title = title

    def set_task_description(self, task_description):
        self._task_description = task_description

    def set_task_status(self, task_status):
        self._task_status = task_status

    def set_project_id(self, project_id):            
        self._project_id = project_id

    def set_assigned_to(self, assigned_to):
        self._assigned_to = assigned_to

    def set_deadline(self, deadline):
        self._deadline = deadline

    def set_created_date(self, created_date):
        self._created_date = created_date

    def get_task_id(self):
        return self._task_id

    def get_title(self):
        return self._title

    def get_task_description(self):
        return self._task_description

    def get_task_status(self):
        return self._task_status

    def get_project_id(self):            
        return self._project_id

    def get_assigned_to(self):
        return self._assigned_to

    def get_deadline(self):
        return self._deadline

    def get_created_date(self):
        return self._created_date

    def __str__(self):
        return f'Id задачи:{self._task_id}, название {self._title}, \
              описание задачи ({self._task_description}), статус {self._task_status}, \
                id проекта:{self._project_id}, id выполняющего:{self._assigned_to}, \
                    дедлайн:{self._deadline}, время создания задания:{self._created_date}'