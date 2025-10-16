import os
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import Connection
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


@pytest.fixture
def anyio_backend():
    return "asyncio"


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
async def test_db_helper(postgres_container):
    from core.models.db_helper import DatabaseHelper

    db_helper = DatabaseHelper(
        url=postgres_container.get_connection_url(),
    )
    async with db_helper.engine.connect() as conn:
        await conn.run_sync(run_alembic_migration)

    yield db_helper

    await db_helper.dispose()


@pytest.fixture(scope="function")
async def session(test_db_helper):
    async for session in test_db_helper.session_getter():
        yield session
        await session.rollback()


@pytest.fixture(scope="session")
async def test_client(test_db_helper):
    from main import app
    from core.models import db_helper

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        app.dependency_overrides[db_helper.session_getter] = (
            test_db_helper.session_getter
        )

        yield ac


@pytest.fixture()
def httpx_client_mock():
    return AsyncMock(spec=AsyncClient)


@pytest.fixture()
def dummy_response_from_nimble():
    from api.v1.contact.schema import (
        NimbleResponse,
        NimbleMeta,
        NimbleFields,
        NimbleResource,
        FieldValue,
    )

    dummy_response = NimbleResponse(
        meta=NimbleMeta(
            page=1,
            pages=1,
            per_page=12,
            total=123,
        ),
        resources=[
            NimbleResource(
                id="abc123",
                record_type="person",
                fields=NimbleFields(
                    email=[
                        FieldValue(value="super@mail.com"),
                        FieldValue(value="stupid@mail.com"),
                    ],
                ),
            ),
        ],
    )
    return dummy_response
