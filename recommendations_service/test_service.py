import requests
import logging
import json

# Настройка логирования
logging.basicConfig(
    filename="test_service.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

BASE_URL = "http://127.0.0.1:8000/recommendations"

def test_service():
    """Тестирование сервиса рекомендаций"""
    # Тест 1: Пользователь без персональных рекомендаций
    payload1 = {"user_id": 9999999, "recent_tracks": []}
    response1 = requests.post(BASE_URL, json=payload1)
    logger.info("Тест 1: Пользователь без персональных рекомендаций")
    logger.info(f"Запрос: {json.dumps(payload1)}")
    logger.info(f"Ответ: {response1.text} - Статус: {response1.status_code}")

    # Тест 2: Пользователь с офлайн-рекомендациями, без онлайн-истории
    payload2 = {"user_id": 1517205, "recent_tracks": []}
    response2 = requests.post(BASE_URL, json=payload2)
    logger.info("Тест 2: Пользователь с офлайн-рекомендациями, без онлайн-истории")
    logger.info(f"Запрос: {json.dumps(payload2)}")
    logger.info(f"Ответ: {response2.text} - Статус: {response2.status_code}")

    # Тест 3: Пользователь с офлайн-рекомендациями и онлайн-историей
    payload3 = {"user_id": 1517205, "recent_tracks": ["53404", "33311009"]}
    response3 = requests.post(BASE_URL, json=payload3)
    logger.info("Тест 3: Пользователь с офлайн-рекомендациями и онлайн-историей")
    logger.info(f"Запрос: {json.dumps(payload3)}")
    logger.info(f"Ответ: {response3.text} - Статус: {response3.status_code}")

    # Тест 4: Пользователь с офлайн-рекомендациями и некорректной онлайн-историей
    payload4 = {"user_id": 1517205, "recent_tracks": ["abc", "def"]}
    response4 = requests.post(BASE_URL, json=payload4)
    logger.info("Тест 4: Пользователь с офлайн-рекомендациями и некорректной онлайн-историей")
    logger.info(f"Запрос: {json.dumps(payload4)}")
    logger.info(f"Ответ: {response4.text} - Статус: {response4.status_code}")

if __name__ == "__main__":
    logger.info("Начало тестирования сервиса")
    test_service()
    logger.info("Тестирование завершено")