import subprocess
import requests
import re 
import shlex
import json

def process_message(message):
    # Проверка на наличие флага "-f" для формирования SQL-запроса и получения результата
    if message.endswith("-f"):
        
        # Убираем флаг "-f" из сообщения
        question_text = message[:-2].strip()
        
        # Формирование SQL-запроса с использованием модели через LM Studio API
        response = requests.post(
            "http://localhost:1234/v1/completions",
            json={
                "model": "ggml-model",  # замените на название модели
                "prompt": f"Ты помощник для формирования SQL-запросов.\n Сформируй SQL запрос для вопроса: '{question_text}'",
                "max_tokens": 100
            }
        )
        
        # Проверяем успешность запроса
        if response.status_code == 200:
            response_text = response.json().get("choices", [{}])[0].get("text", "").strip()
            # Вывод сформированного ответа для отладки
            #print(f"Сформированный ответ: {response_text}") 
            
            # Извлечение SQL-запроса из ответа
            sql_query_matches = re.findall(r'```sql\n(.*?)\n```', response_text, re.DOTALL)
            if sql_query_matches:
                sql_query = sql_query_matches[0].strip()  # Берем только первый найденный SQL-запрос
            else:
                print("Ошибка: модель вернула пустой SQL-запрос.")
                return "Ошибка: пустой SQL-запрос."
            
            print(f"Извлечённый SQL-запрос: {sql_query}")  # Вывод извлечённого SQL-запроса для отладки
        else:
            print(f"Ошибка: {response.status_code} - {response.text}")
            return "Ошибка выполнения запроса к модели LM Studio"
        
        
        # Запуск db_zapros.py для выполнения SQL-запроса
        result_zapros = subprocess.run(
            ["python", "db_zapros.py", sql_query],
            capture_output=True,
            text=True,
            check=True,
            shell = True
        )
        # Обработка вывода
        print(f"Результат выполнения db_zapros.py: {result_zapros.stdout}")  # Отладочное сообщение
        
        # Попробуем вывести данные, даже если это не JSON
        result_output = result_zapros.stdout.strip()  # Убираем лишние пробелы и символы новой строки
        # Отладка
        #print(f"Обработанный вывод: {result_output}")
        
        try:
            # Пытаемся загрузить результаты как JSON
            result_data = json.loads(result_output)
            print(f"Извлеченные данные: {result_data}")  # Отладочное сообщение
            
            # Извлечение значения из результата
            # Извлечение всех значений из результата
            values = []
            for row in result_data:
                for value in row:
                    values.append(value)
            
            full_message = f"Ответь на: {question_text} Выполняя sql запрос: {sql_query} Получили: {', '.join(map(str, values))}"
        except json.JSONDecodeError:
            full_message = f"Ответь на: {question_text} Выполняя sql запрос: {sql_query} Ошибка при получении результата: {result_output}"
        print(full_message)
    
    # Запуск db_vopros.py для финальной генерации ответа с учетом данных из БД
    result_vopros = subprocess.run(
        ["python", "db_vopros.py", full_message],  # Разбиение строки
        capture_output=True,
        text=True,
        check=True,
        shell=True
    )
    # Возвращаем финальный ответ
    return result_vopros.stdout
    

# Пример вызова
message = "Сколько в нашей базе данных clients? -f"
try:
    final_output = process_message(message)
    print(final_output)
except subprocess.CalledProcessError as e:
    print(f"Ошибка выполнения: {e}")
