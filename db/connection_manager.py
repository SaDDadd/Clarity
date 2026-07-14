import pymysql 
from config.db_config import config

# query - SQL запрос
# params - набор данных, которые вставляем вместо %s

# Отвечает за config базы
class DatabaseHelper:
    def __init__(self):
        self.config = config

    def connect(self):
        try:
            connection = pymysql.connect(**self.config)
            return connection
        except pymysql.MySQLError as error:
            print(f'Ошибка подключения: {error}')
            return None
    
    def execute_query(self, query, params=None): # Выполнение запросов и возращение затронутых строк
        connection = self.connect() 

        try:
            if connection is None:
                return 
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('INSERT'): # Выводим либо ID записей, лиюо количество записей
                    result = cursor.lastrowid 
                else:
                    result = cursor.rowcount
                connection.commit()
                return result
        except pymysql.MySQLError as error:
            connection.rollback()
            print(f'Ошибка с запросом {error}')
        finally:
            if connection is None:
                return 
            connection.close()

    def fetch_all(self, query, params=None): # Забрать все строки результата запроса 
        result = None
        connection = self.connect()
        try:
            if connection is None:
                return
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except pymysql.MySQLError as error:
            connection.rollback()
            print(f'Ошибка с выводом результата {error}')
        finally:
            if connection is None:
                return
            connection.close()
        
    def fetch_one(self, query, params=None): # Забрать одну строку результата запроса
        result = None
        connection = self.connect()
        try:
            if connection is None:
                return
            with connection.cursor() as cursor:
                cursor.execute(query, params) 
                result = cursor.fetchone()
                return result
        except pymysql.MySQLError as error:
            connection.rollback()
            print(f'Ошибка с выводом результата {error}')
        finally:
            if connection is None:
                return 
            connection.close()
