import os
import pymysql 
from dotenv import load_dotenv

load_dotenv() # Загрузка переменных из .env

config = {'host':os.getenv('DB_HOST', 'localhost'), \
          'port':int(os.getenv('DB_PORT', 3306)), \
          'user':os.getenv('DB_USER', 'root'), \
          'password':os.getenv('DB_PASSWORD', '2007'), \
          'database':os.getenv('DB_NAME', 'task_to_do'), \
          'charset':os.getenv('DB_CHARSET', 'utf8mb4'), \
          'cursorclass':pymysql.cursors.DictCursor}