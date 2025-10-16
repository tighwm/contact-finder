import os
from pathlib import Path

import pytest
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer
from alembic.config import Config
from alembic import command


os.environ.update(
    {
        "APP_CONFIG__TASKIQ__URL": "amqp://guest:guest@localhost:5672//",
        "APP_CONFIG__NIMBLE__TOKEN": "",
    }
)

here = Path(__file__).resolve()
alembic_ini = here.parent.parent / "src" / "alembic.ini"


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(
        username="nimble",
        password="secret",
        dbname="nimble",
        driver="asyncpg",
    ) as postgres:
        os.environ["APP_CONFIG__DB__URL"] = postgres.get_connection_url()
        yield postgres


def run_alembic_migration(
    conn: Connection,
    alembic_ini_path: Path = alembic_ini,
    revision: str = "head",
):
    config = Config(alembic_ini_path)
    command.upgrade(config, revision)


@pytest.fixture(scope="session")
async def engine(postgres_container):
    engine = create_async_engine(
        url=postgres_container.get_connection_url(),
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
