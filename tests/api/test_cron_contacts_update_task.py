from unittest.mock import Mock

import pytest
from sqlalchemy import select


@pytest.mark.anyio
async def test_cron_contacts_update_task(
    httpx_client_mock,
    session,
    dummy_response_from_nimble,
):
    from tasks.cron_contact_update import update_contacts_per_day
    from core.models import Contact

    fake_response = dummy_response_from_nimble.model_dump(by_alias=True)

    httpx_client_mock.get.return_value = Mock(json=lambda: fake_response)

    await update_contacts_per_day(httpx_client_mock, session)

    stmt = select(Contact)
    result_scalar = await session.scalars(stmt)
    contacts = result_scalar.all()

    assert (
        contacts[0].email
        == dummy_response_from_nimble.resources[0].fields.email[0].value
    )
