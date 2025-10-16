async def test_query_request(test_client, session):
    from core.models import Contact
    from api.v1.contact.schema import ContactSchema

    contacts = [
        Contact(first_name="ken", last_name="jensen"),
        Contact(first_name="Ken", last_name="kaneki", email="deadinside@mail.com"),
        Contact(first_name="sasha", last_name="grey"),
    ]
    for con in contacts:
        session.add(con)
    await session.commit()

    response = await test_client.get(
        url="/api/v1/contacts/search",
        params={"q": "ken"},
    )

    assert response.status_code == 200
    result = response.json()
    expected = [
        ContactSchema.model_validate(con).model_dump(by_alias=True)
        for con in contacts
        if con.first_name != "sasha"
    ]
    assert result == expected

    for con in contacts:
        await session.delete(con)
    await session.commit()
