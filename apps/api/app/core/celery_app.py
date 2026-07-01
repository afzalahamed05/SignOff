from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.ai_worker"]
)

celery_app.conf.update(
    task_track_started=True,
    task_time_limit=300,  # 5 mins max for AI tasks
    timezone="UTC",
    enable_utc=True,
)