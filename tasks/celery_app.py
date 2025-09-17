# tasks/celery_app.py
import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "bot_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.beat_scheduler = "redbeat.RedBeatScheduler"  # optional if using redbeat
