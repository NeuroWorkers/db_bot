import os
import psycopg2
from psycopg2 import sql
import sys
import json
from dotenv import load_dotenv

load_dotenv()
# Загрузка переменных окружения
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')

def execute_query(query_str):
    # Выводим отладочную информацию в stderr
    print(f"Выполняется SQL-запрос: {query_str}", file=sys.stderr)
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        cursor = connection.cursor()

        # Выполнение запроса
        cursor.execute(sql.SQL(query_str))
        
        # Получение результата (если это SELECT-запрос)
        if query_str.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            # Возвращаем результаты в формате JSON
            return json.dumps(results)
        else:
            # Применение изменений для INSERT, UPDATE, DELETE
            connection.commit()
            return json.dumps({"status": "success"})
    
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})
    
    finally:
        # Закрытие соединения с БД
        if connection:
            cursor.close()
            connection.close()


# Проверяем, передан ли SQL-запрос в качестве аргумента командной строки
if len(sys.argv) > 1:
    query_str = sys.argv[1]  # Получаем SQL-запрос из аргументов
    result = execute_query(query_str)
    print(result)
else:
    print("Не передан SQL-запрос.", file=sys.stderr)