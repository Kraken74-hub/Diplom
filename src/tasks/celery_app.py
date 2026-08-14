from celery import Celery
from config.settings import settings
import src.tasks.scheduler

# Инициализация Celery с подключением к Redis
celery = Celery(
    "wb_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.tasks.workers"]
)
celery.conf.timezone = 'UTC'