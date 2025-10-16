from sqlalchemy import select


async def test_get_contacts_by_query(session):
    from core.models import Contact
    from api.v1.contact.crud import get_contacts_by_query

    ryan = Contact(first_name="ryan", last_name="gosling")
    thomas = Contact(first_name="thomas", last_name="gosling")

    session.add(ryan)
    session.add(thomas)
    await session.flush()

    query = "ryan"

    result = await get_contacts_by_query(session, query)

    assert result == [ryan]


async def test_batch_insert_contacts(session):
    from api.v1.contact.crud import batch_insert_contacts

    contacts = [
        {
            "first_name": "Karl",
            "last_name": "Marks",
            "nimble_id": "id",
        },
        {
            "first_name": "Mega",
            "last_name": "Mind",
            "nimble_id": "megaid",
        },
    ]
    result = await batch_insert_contacts(
        session,
        contacts=contacts,
    )

    assert len(result) == 2


async def test_batch_insert_contacts_with_conflict(session):
    from core.models import Contact
    from api.v1.contact.crud import batch_insert_contacts

    sasha = Contact(
        first_name="sasha",
        last_name="cover",
        nimble_id="id",
    )

    session.add(sasha)
    await session.flush()

    contacts = [
        {
            "first_name": "Karl",
            "last_name": "Marks",
            "nimble_id": "id",
        },
        {
            "first_name": "Mega",
            "last_name": "Mind",
            "nimble_id": "megaid",
        },
    ]
    result = await batch_insert_contacts(
        session,
        contacts=contacts,
        on_conflict_do_update_index_elements=["nimble_id"],
    )

    await session.refresh(sasha)
    stmt = select(Contact)
    scalar_res = await session.scalars(stmt)

    #  check the len because it will show whether the row was created or updated
    assert len(scalar_res.all()) == len(result)
