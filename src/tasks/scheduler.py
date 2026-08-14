from celery.schedules import crontab
from src.tasks.celery_app import celery

# Настройка планировщика Celery Beat: запуск задачи проверки каждый час в 00 минут
celery.conf.beat_schedule = {
    'check-wb-prices-hourly': {
        'task': 'src.tasks.workers.check_prices',
        'schedule': crontab(minute=0),
    },
}