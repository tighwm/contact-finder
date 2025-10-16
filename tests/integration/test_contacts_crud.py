async def test_get_contacts_by_query(session):
    from api.v1.contact.crud import get_contacts_by_query
    from core.models import Contact

    ryan = Contact(first_name="ryan", last_name="gosling")
    thomas = Contact(first_name="thomas", last_name="gosling")

    session.add(ryan)
    session.add(thomas)
    await session.flush()

    query = "ryan"

    result = await get_contacts_by_query(session, query)

    assert result == [ryan]
