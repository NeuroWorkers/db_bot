import os
import sys
import json
import requests

def send_message_to_api(message):
    # Формируем JSON-запрос
    response = requests.post(
        "http://localhost:1234/v1/completions",
        json={
            "model": "ggml-model",  # замените на название модели
            "prompt": f"{message}",
            "max_tokens": 100
        }
    )
  
    # Проверка успешности запроса
    if response.status_code == 200:
        response_text = response.json().get("choices", [{}])[0].get("text", "").strip()
        print(f"Сформированный ответ: {response_text}")  # Вывод сформированного ответа для отладки
    else:
        print(f"Ошибка: {response.status_code} - {response.text}")
        return "Ошибка выполнения запроса к модели LM Studio"

def main():
    # Получаем сообщение из аргументов командной строки
    
    if len(sys.argv) > 1:
        full_message = sys.argv[1]  # Объединяем все аргументы в одно сообщение
    else:
        print("Ошибка: Необходимо передать сообщение.")
        sys.exit(1)
    
    # Отправка сообщения
    answer = send_message_to_api(full_message)
    
    if answer:
        print(answer)

if __name__ == "__main__":
    main()
