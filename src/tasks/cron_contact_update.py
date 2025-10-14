import logging
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends

from core import broker
from core.models import db_helper

log = logging.getLogger(__name__)


@broker.task(schedule=[{"cron": "* * * * *"}])
async def update_contacts_per_day(
    session: Annotated[
        AsyncSession,
        TaskiqDepends(db_helper.session_getter),
    ],
):
    log.info("Im dummy task! I got a session `%s`", session)
