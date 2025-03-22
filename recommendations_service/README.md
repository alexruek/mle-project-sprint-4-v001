# Сервис рекомендаций

Это микросервис на основе FastAPI для выдачи рекомендаций музыкальных треков. Он сочетает офлайн-рекомендации (предварительно рассчитанные с помощью ALS и CatBoost) с онлайн-рекомендациями (основанными на недавней истории прослушиваний пользователя).

## Требования

- Python 3.10+
- Виртуальное окружение с зависимостями:
  ```bash
  pip install fastapi uvicorn pandas boto3 pydantic python-dotenv
  
    Файл .env в родительской директории с переменными:
    text

    AWS_ACCESS_KEY_ID=ваш_ключ
    AWS_SECRET_ACCESS_KEY=ваш_секрет
    S3_BUCKET_NAME=s3-student-mle-20240325-963286077c

Установка

    Склонируйте репозиторий или скопируйте файлы проекта:
    text

recommendations_service/
├── recommendations_service.py
├── test_service.py
└── README.md
Перейдите в директорию recommendations_service:
bash
cd recommendations_service
Активируйте виртуальное окружение:
bash

    source ../venv/bin/activate  # Для Windows: ..\venv\Scripts\activate

Запуск сервиса

Запустите сервис FastAPI:
bash
uvicorn recommendations_service:app --reload

Сервис будет доступен по адресу http://127.0.0.1:8000.
API-эндпоинт

    POST /recommendations
        Тело запроса:
        json

{
  "user_id": целое_число,
  "recent_tracks": ["item_id1", "item_id2", ...]  # Необязательный список недавних треков
}
Ответ:
json
{
  "user_id": целое_число,
  "recommendations": ["item_id1", "item_id2", ..., "item_id10"]
}
Примеры:

    Пользователь с офлайн-рекомендациями:
    bash

curl -X POST "http://127.0.0.1:8000/recommendations" -H "Content-Type: application/json" -d '{"user_id": 1517205, "recent_tracks": []}'
Пользователь с онлайн-историей:
bash

            curl -X POST "http://127.0.0.1:8000/recommendations" -H "Content-Type: application/json" -d '{"user_id": 9999999, "recent_tracks": ["53404", "33311009"]}'

Стратегия смешивания рекомендаций

Сервис комбинирует офлайн- и онлайн-рекомендации следующим образом:

    Офлайн-рекомендации: Предварительно рассчитаны с использованием ALS и CatBoost, хранятся в s3://s3-student-mle-20240325-963286077c/recsys/recommendations/recommendations.parquet. Если для пользователя нет офлайн-рекомендаций, используются топ-10 популярных треков из items_features.parquet.
    Онлайн-рекомендации: Формируются на основе recent_tracks из запроса. Сервис определяет наиболее частые жанры недавних треков и выбирает топ-10 популярных треков из этих жанров.
    Логика смешивания:
        Если recent_tracks пустой, возвращаются топ-10 офлайн-рекомендаций.
        Если recent_tracks указан, берётся 5 треков из офлайн-рекомендаций и 5 из онлайн-рекомендаций.
        Дубликаты удаляются, и список дополняется до 10 треков дополнительными офлайн-рекомендациями при необходимости.
    Запасной вариант: Если нет ни офлайн-, ни онлайн-рекомендаций (например, некорректные recent_tracks), возвращаются топ-10 популярных треков.

Тестирование

Для тестирования сервиса используйте скрипт test_service.py:

    Убедитесь, что сервис запущен:
    bash

uvicorn recommendations_service:app --reload
Запустите тесты:
bash

    python test_service.py
    Проверьте результаты в файле test_service.log. Тесты охватывают:
        Пользователь без персональных рекомендаций (user_id=9999999, без истории).
        Пользователь с офлайн-рекомендациями, без онлайн-истории (user_id=1517205, recent_tracks=[]).
        Пользователь с офлайн-рекомендациями и онлайн-историей (user_id=1517205, recent_tracks=["53404", "33311009"]).

Результаты тестирования сохраняются в test_service.log.