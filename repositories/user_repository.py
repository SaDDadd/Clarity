import pymysql
from db.connection_manager import DatabaseHelper
from models.user import User

class UserRepository:
    def __init__(self):
        self.db_helper = DatabaseHelper()

    def create_user(self, username, email, password): # Создание пользователя
        sql = 'INSERT INTO users (username, email, ' \
        'password_hash)' \
        'VALUES (%s, %s, %s);'

        return self.db_helper.execute_query(sql, (username, email, password))
    
    def get_by_id(self, user_id): # Возвращаем всю информацию про пользователя по id 
        sql = 'SELECT * FROM users WHERE user_id = (%s)'
        row = self.db_helper.fetch_one(sql, (user_id,))
        return User.from_dict_or_none(row)

    def get_by_username(self, username): # Возращает всю информацию про пользователя по имени
        sql = 'SELECT * FROM users WHERE  username = (%s)'
        row = self.db_helper.fetch_one(sql, (username,))
        return User.from_dict_or_none(row)

    def delete_user(self, user_id): # Удаление пользователя
        sql = 'DELETE FROM users WHERE user_id = (%s)'

        return self.db_helper.execute_query(sql, (user_id,))

    def check_user_exists(self, user_id): # Проверка существования пользователя
        sql = 'SELECT user_id FROM users WHERE user_id = (%s)'

        return self.db_helper.fetch_one(sql, (user_id,))