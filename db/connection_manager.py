import pymysql
from config.db_config import config

class DatabaseHelper:
    def __init__(self) -> None: # Инициализация с конфигом
        self.config = config

    def connect(self) -> pymysql.connections.Connection | None: # Установить соединение с БД
        try:
            connection = pymysql.connect(**self.config)
            return connection
        except pymysql.MySQLError as error:
            print(f'Ошибка подключения: {error}')
            return None
    
    def execute_query(self, query: str, params: tuple | None = None) -> int | None: # Выполнить запрос (INSERT/UPDATE/DELETE) и вернуть количество затронутых строк или ID
        connection = self.connect()
        try:
            if connection is None:
                return None
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('INSERT'):
                    result = cursor.lastrowid
                else:
                    result = cursor.rowcount
                connection.commit()
                return result
        except pymysql.MySQLError as error:
            connection.rollback()
            print(f'Ошибка с запросом {error}')
            return None
        finally:
            if connection is not None:
                connection.close()

    def fetch_all(self, query: str, params: tuple | None = None) -> list[dict] | None: # Выполнить SELECT и вернуть все строки
        connection = self.connect()
        try:
            if connection is None:
                return None
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except pymysql.MySQLError as error:
            connection.rollback()
            print(f'Ошибка с выводом результата {error}')
            return None
        finally:
            if connection is not None:
                connection.close()
        
    def fetch_one(self, query: str, params: tuple | None = None) -> dict | None: # Выполнить SELECT и вернуть одну строку
        connection = self.connect()
        try:
            if connection is None:
                return None
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result
        except pymysql.MySQLError as error:
            connection.rollback()
            print(f'Ошибка с выводом результата {error}')
            return None
        finally:
            if connection is not None:
                connection.close()

    def execute_transactions(self, queries: list[tuple[str, tuple]]) -> list[int] | None: # Выполнить несколько запросов в транзакции
        if len(queries) == 0:
            return None
        connection = self.connect()
        try:
            if connection is None:
                return None
            with connection.cursor() as cursor:
                connection.autocommit = False
                result = []
                for item in queries:
                    cursor.execute(item[0], item[1])
                    if item[0].strip().upper().startswith('INSERT'):
                        result.append(cursor.lastrowid)
                    else:
                        result.append(cursor.rowcount)
                connection.commit()
                return result
        except pymysql.MySQLError as error:
            connection.rollback()
            print(f'Ошибка с выводом результата {error}')
            return None
        finally:
            if connection is not None:
                connection.close()