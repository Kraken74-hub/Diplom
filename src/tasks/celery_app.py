from celery import Celery
from config.settings import settings

celery = Celery(
    "wb_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.tasks.workers"]
)

celery.conf.timezone = 'UTC'

celery.conf.beat_schedule = {
    "my-periodic-task": {
        "task": "src.tasks.workers.check_prices",
        "schedule": 60.0,
    },
}