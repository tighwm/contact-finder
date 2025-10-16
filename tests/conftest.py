import os
from pathlib import Path

import pytest
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from alembic.config import Config
from alembic import command
from starlette.testclient import TestClient


os.environ.update(
    {
        "APP_CONFIG__DB__URL": "postgresql+asyncpg://nimble:secret@localhost:5432/nimble",
        "APP_CONFIG__TASKIQ__URL": "amqp://guest:guest@localhost:5672//",
    }
)

from main import app
from core.config import settings
from core.models import db_helper

here = Path(__file__).resolve()
alembic_ini = here.parent.parent / "src" / "alembic.ini"


def run_alembic_migration(
    conn: Connection,
    alembic_ini_path: Path = alembic_ini,
    revision: str = "head",
):
    config = Config(alembic_ini_path)
    command.upgrade(config, revision)


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        url=str(settings.db.url),
        echo=False,
    )

    async with engine.connect() as conn:
        await conn.run_sync(run_alembic_migration)

    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def session_maker(engine):
    session_maker = async_sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return session_maker


@pytest.fixture(scope="function")
async def session(session_maker):
    async with session_maker() as async_session:
        yield async_session
        await async_session.rollback()


async def override_session_getter():
    session = db_helper.local_session()
    yield session
    await session.rollback()
    await session.aclose()


@pytest.fixture(scope="session")
def client(engine):
    test_client = TestClient(app)
    app.dependency_overrides[db_helper.session_getter] = override_session_getter  # noqa
    yield test_client
