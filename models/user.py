import datetime

class User:
    def __init__(self, user_id: int, username: str, email: str, password_hash: str,
                 created_date: datetime.datetime) -> None: # Конструктор
        self._user_id = user_id 
        self._username = username
        self._email = email 
        self._password_hash = password_hash
        self._created_date = created_date

    @classmethod 
    def from_dict(cls, data: dict) -> "User": # Создать объект из словаря
        return cls(user_id = data.get('user_id'), username = data.get('username'),
                   email = data.get('email'), password_hash = data.get('password_hash'),
                    created_date = data.get('created_date'))

    @classmethod
    def from_dict_or_none(cls, data: dict | None) -> "User" | None: # Создать объект или вернуть None
        return cls.from_dict(data) if data else None

    def set_user_id(self, user_id: int) -> None: # Установить ID пользователя
        self._user_id = user_id

    def set_username(self, username: str) -> None: # Установить имя пользователя
        self._username = username 

    def set_email(self, email: str) -> None: # Установить email
        self._email = email

    def set_password_hash(self, password_hash: str) -> None: # Установить хэш пароля
        self._password_hash = password_hash

    def set_created_date(self, created_date: datetime.datetime) -> None: # Установить дату создания
        self._created_date = created_date

    def get_user_id(self) -> int: # Получить ID пользователя
        return self._user_id

    def get_username(self) -> str: # Получить имя пользователя
        return self._username

    def get_email(self) -> str: # Получить email
        return self._email

    def get_password_hash(self) -> str: # Получить хэш пароля
        return self._password_hash

    def get_created_date(self) -> datetime.datetime: # Получить дату создания
        return self._created_date

    def __str__(self) -> str: # Строковое представление
        return f'Id пользователя:{self._user_id}, имя пользователя {self._username}, \
              email:{self._email}, время создания аккаунта:{self._created_date}'