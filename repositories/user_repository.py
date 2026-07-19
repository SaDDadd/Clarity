import bcrypt
from db.connection_manager import DatabaseHelper
from models.user import User
from decorators.decorators import log

class UserRepository:
    def __init__(self):
        self.db_helper = DatabaseHelper()

    @log
    def create_user(self, username, email, password): # Создание пользователя
        sql = 'INSERT INTO users (username, email, ' \
        'password_hash)' \
        'VALUES (%s, %s, %s);'
        return self.db_helper.execute_query(sql, (username, email, password))

    @log
    def get_by_id(self, user_id): # Возвращаем всю информацию про пользователя по id 
        sql = 'SELECT * FROM users WHERE user_id = (%s)'
        row = self.db_helper.fetch_one(sql, (user_id,))
        return User.from_dict_or_none(row)

    @log
    def get_by_username(self, username): # Возращает всю информацию про пользователя по имени
        sql = 'SELECT * FROM users WHERE  username = (%s)'
        row = self.db_helper.fetch_one(sql, (username,))
        return User.from_dict_or_none(row)

    @log
    def get_by_email(self, email): # Возращает всю информацию про пользователя по email
        sql = 'SELECT * FROM users WHERE email = (%s)'
        row = self.db_helper.fetch_one(sql, (email,))
        return User.from_dict_or_none(row)

    def delete_user(self, user_id): # Удаление пользователя
        sql = 'DELETE FROM users WHERE user_id = (%s)'
        return self.db_helper.execute_query(sql, (user_id,))

    def check_user_exists(self, user_id): # Проверка существования пользователя
        sql = 'SELECT user_id FROM users WHERE user_id = (%s)'
        return self.db_helper.fetch_one(sql, (user_id,))

    def check_user_exists_by_username(self, username): # Проверка сущетвования пользователя по имени
        sql = 'SELECT user_id FROM users WHERE username = (%s)'
        return self.db_helper.fetch_one(sql, (username,))

    def check_user_exists_by_email(self, email): # Проверка существования пользователя по email
        sql = 'SELECT user_id FROM users WHERE email = (%s)'
        return self.db_helper.fetch_one(sql, (email,))

    def check_user_correct_password_by_email(self, email, password): # Проверка правильного пароля по email
        sql = 'SELECT password_hash FROM users WHERE email = (%s)'
        row = self.db_helper.fetch_one(sql, (email,))
        if row is None:
            return False
        stored_hash = row['password_hash'].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

    def check_user_correct_password_by_username(self, username, password): # Проверка правильности пароля по имени
        sql = 'SELECT password_hash FROM users WHERE username = (%s)'

        row = self.db_helper.fetch_one(sql, (username,))
        if row is None:
            return False 
        stored_hash = row['password_hash'].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)