from celery import Celery
from core.config import settings

celery_app = Celery(
    "worker",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

celery_app.conf.task_routes = {
    "worker.tasks.*": "main-queue",
}

celery_app.autodiscover_tasks(["services.ingestion"])
