from celery import Celery

from mcp_foundry.core.config import settings

celery_app = Celery(
    "mcp_foundry",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["mcp_foundry.scraping.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
