from typing import Any, Sequence

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.models import Contact


async def get_contacts_by_query(
    session: AsyncSession,
    query: str,
) -> Sequence[Contact]:
    to_search = func.to_tsvector(
        "english",
        Contact.first_name
        + " "
        + Contact.last_name
        + " "
        + Contact.email
        + " "
        + Contact.description,
    )
    condition = to_search.op("@@")(func.plainto_tsquery("english", query))

    stmt = select(Contact).where(condition)
    result = await session.execute(stmt)
    return result.scalars().all()


async def batch_insert_contacts(
    session: AsyncSession,
    contacts: list[dict[str, Any]],
    on_conflict_do_update_index_elements: list[str] = None,
) -> Sequence[int]:
    stmt = insert(Contact).values(contacts)
    if on_conflict_do_update_index_elements:
        stmt = stmt.on_conflict_do_update(
            index_elements=on_conflict_do_update_index_elements,
            set_={
                "first_name": stmt.excluded.first_name,
                "last_name": stmt.excluded.last_name,
                "email": stmt.excluded.email,
                "description": stmt.excluded.description,
            },
        )
    result = await session.execute(stmt.returning(Contact.id))
    return result.scalars().all()
