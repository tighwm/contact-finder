__all__ = (
    "broker",
    "scheduler",
)

import logging

import taskiq_fastapi
from taskiq import TaskiqEvents, TaskiqState, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker
from core.config import settings
from core.models import db_helper

log = logging.getLogger(__name__)

broker = AioPikaBroker(url=str(settings.taskiq.url))
taskiq_fastapi.init(broker, "main:app")

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def on_startup(state: TaskiqState):
    logging.basicConfig(
        level=settings.logging.log_level_value,
        format=settings.taskiq.log_format,
        datefmt=settings.logging.date_format,
    )
    log.info("Worker startup complete. Got: %s", state)
