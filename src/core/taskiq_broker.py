__all__ = (
    "broker",
    "scheduler",
)

import logging
import os

import httpx
import taskiq_fastapi
from taskiq import TaskiqEvents, TaskiqState, TaskiqScheduler, InMemoryBroker
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker

log = logging.getLogger(__name__)

env = os.environ.get("ENVIRONMENT")


if env and env == "pytest":
    broker = InMemoryBroker()
else:
    from core.config import settings

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

    state.client = httpx.AsyncClient(
        base_url=settings.nimble.base_url,
        headers={"Authorization": f"Bearer {settings.nimble.token}"},
    )
    log.info("Worker startup complete. Got: %s", state)


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def on_shutdown(state: TaskiqState):
    client: httpx.AsyncClient = state.client
    await client.aclose()
