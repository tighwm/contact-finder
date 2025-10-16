import pytest


async def test_db_helper_session_getter_rollback(postgres_container):
    from core.models.db_helper import DatabaseHelper
    from sqlalchemy import text

    db_helper = DatabaseHelper(url=postgres_container.get_connection_url())

    async for session in db_helper.session_getter():
        stmt = text(
            "CREATE TABLE IF NOT EXISTS test_rollback ("
            "id SERIAL PRIMARY KEY,"
            "value TEXT"
            ")"
        )
        await session.execute(stmt)

    async def dummy_error(session):
        stmt = text("INSERT INTO test_rollback (value) VALUES ('boom')")
        await session.execute(stmt)
        raise ValueError("Im dummy")

    with pytest.raises(ValueError):
        async for session in db_helper.session_getter():
            await dummy_error(session)

    async for session in db_helper.session_getter():
        stmt = text("SELECT COUNT(*) FROM test_rollback")
        result = await session.execute(stmt)
        result = result.scalar()
        assert result == 0

        drop_stmt = text("DROP TABLE test_rollback")
        await session.execute(drop_stmt)
