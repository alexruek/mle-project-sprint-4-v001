from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import pandas as pd
import boto3
from io import BytesIO

# Загрузка .env из родительской директории
load_dotenv(dotenv_path="../.env")

# Инициализация S3 клиента
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    endpoint_url="https://storage.yandexcloud.net"
)

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
if not S3_BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME не найден в .env")

# Пути к файлам в S3
OFFLINE_RECS_PATH = "s3://s3-student-mle-20240325-963286077c/recsys/recommendations/recommendations.parquet"
ITEMS_FEATURES_PATH = "s3://s3-student-mle-20240325-963286077c/recsys/features/items_features.parquet"


def load_data_from_s3(s3_path):
    """Загрузка parquet-файла из S3 с преобразованием в BytesIO"""
    key = s3_path.split(f"{S3_BUCKET_NAME}/")[1]
    obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
    buffer = BytesIO(obj["Body"].read())
    return pd.read_parquet(buffer)


# Загрузка данных при старте сервиса
try:
    offline_recs = load_data_from_s3(OFFLINE_RECS_PATH)
    items_features = load_data_from_s3(ITEMS_FEATURES_PATH)
    top_popular = (items_features
                   .sort_values("track_popularity", ascending=False)
                   ["item_id"]
                   .head(10)
                   .tolist())
except Exception as e:
    raise RuntimeError(f"Ошибка загрузки данных из S3: {str(e)}")

app = FastAPI()


# Модель для валидации тела запроса
class RecommendationRequest(BaseModel):
    user_id: int
    recent_tracks: list[str] = []


def get_offline_recommendations(user_id: int) -> list:
    """Получение офлайн-рекомендаций для пользователя"""
    user_recs = offline_recs[offline_recs["user_id"] == user_id]
    if not user_recs.empty:
        return user_recs["item_id"].tolist()
    return top_popular


def get_online_recommendations(recent_tracks: list[str]) -> list:
    """Получение онлайн-рекомендаций на основе недавних треков"""
    if not recent_tracks:
        return []

    try:
        recent_tracks = [int(track) for track in recent_tracks]
    except ValueError:
        return top_popular

    recent_items = items_features[items_features["item_id"].isin(recent_tracks)]
    if recent_items.empty:
        return top_popular

    main_genres = recent_items["main_genre"].mode().tolist()
    if not main_genres:
        return top_popular

    online_recs = (items_features[items_features["main_genre"].isin(main_genres)]
                   .sort_values("track_popularity", ascending=False)
                   ["item_id"]
                   .head(10)
                   .tolist())
    return online_recs


def blend_recommendations(offline_recs: list, online_recs: list) -> list:
    """Смешивание офлайн- и онлайн-рекомендаций"""
    if not online_recs:  # Если нет онлайн-рекомендаций
        return offline_recs[:10]

    # Берем по 5 треков из каждого источника
    offline_half = offline_recs[:5]
    online_half = online_recs[:5]

    # Объединяем и убираем дубликаты, дополняя до 10 треков
    blended = list(dict.fromkeys(offline_half + online_half))
    if len(blended) < 10:
        remaining = 10 - len(blended)
        # Дополняем из оставшихся офлайн-рекомендаций
        additional = [item for item in offline_recs[5:] if item not in blended][:remaining]
        blended.extend(additional)

    return blended[:10]


@app.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """
    Получение смешанных рекомендаций с учётом офлайн- и онлайн-истории.
    """
    offline_recs = get_offline_recommendations(request.user_id)
    online_recs = get_online_recommendations(request.recent_tracks)
    recommendations = blend_recommendations(offline_recs, online_recs)
    return {"user_id": request.user_id, "recommendations": recommendations}