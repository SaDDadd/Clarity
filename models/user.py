class User:
    def __init__(self, user_id, username, email, password_hash, \
                 created_date):
        self._user_id = user_id 
        self._username = username
        self._email = email 
        self._password_hash = password_hash
        self._created_date = created_date

    @classmethod 
    def from_dict(cls, data: dict): # Разбиение словаря после запроса
        return cls(user_id = data.get('user_id'), username = data.get('username'), \
                   email = data.get('email'), password_hash = data.get('password_hash'), \
                    created_date = data.get('created_date'))

    @classmethod
    def from_dict_or_none(cls, data): # Проверка, если в запросе выводиться None
        return cls.from_dict(data) if data else None

    def set_user_id(self, user_id):
        self._user_id = user_id

    def set_username(self, username):
        self._username = username 

    def set_email(self, email):
        self._email = email

    def set_password_hash(self, password_hash):
        self._password_hash = password_hash

    def set_created_date(self, created_date):
        self._created_date = created_date

    def get_user_id(self):
        return self._user_id

    def get_username(self):
        return self._username

    def get_email(self):
        return self._email

    def get_password_hash(self):
        return self._password_hash

    def get_created_date(self):
        return self._created_date

    def __str__(self):
        return f'Id пользователя:{self._user_id}, имя пользователя {self._username}, \
              email:{self._email}, время создания аккаунта:{self._created_date}'