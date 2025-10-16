from unittest.mock import AsyncMock, Mock

import pytest
from httpx import HTTPStatusError


def test_extract_contacts_from_response_as_dicts(dummy_response_from_nimble):
    from tasks.cron_contact_update import extract_contacts_from_response_as_dicts

    result = extract_contacts_from_response_as_dicts(dummy_response_from_nimble)

    assert result == [
        {
            "first_name": None,
            "last_name": None,
            "email": "super@mail.com",
            "nimble_id": "abc123",
            "description": None,
        }
    ]


async def test_fetch_contacts(httpx_client_mock):
    from tasks.cron_contact_update import fetch_contacts
    from api.v1.contact.schema import NimbleResponse

    response_mock = Mock(status_code=200)
    fake_json = {
        "meta": {"page": 1, "pages": 2, "per_page": 30, "total": 100},
        "resources": [],
    }
    # adding extra field to test its removal
    fake_json_with_extra = fake_json.copy()
    fake_json_with_extra["extra"] = "delete me"

    response_mock.json.return_value = fake_json_with_extra
    httpx_client_mock.get.return_value = response_mock

    result = await fetch_contacts(httpx_client_mock)

    assert isinstance(result, NimbleResponse)
    assert result.model_dump() == fake_json


async def test_fetch_contacts_error(httpx_client_mock):
    from tasks.cron_contact_update import fetch_contacts

    response_mock = Mock()
    response_mock.raise_for_status.side_effect = HTTPStatusError(
        message="some error",
        request=Mock(),
        response=Mock(),
    )
    httpx_client_mock.get.return_value = response_mock

    with pytest.raises(HTTPStatusError):
        await fetch_contacts(httpx_client_mock)

    assert httpx_client_mock.get.call_count == 3


async def test_fetch_contacts_pages_agen(httpx_client_mock, monkeypatch):
    from tasks.cron_contact_update import fetch_contacts_pages_agen
    from api.v1.contact.schema import NimbleResponse, NimbleMeta

    fake_responses = [
        NimbleResponse(
            meta=NimbleMeta(
                pages=2,
                page=1,
                per_page=10,
                total=20,
            )
        ),
        NimbleResponse(
            meta=NimbleMeta(
                pages=2,
                page=2,
                per_page=10,
                total=20,
            )
        ),
    ]
    fetch_contacts_mock = AsyncMock(side_effect=fake_responses)
    monkeypatch.setattr("tasks.cron_contact_update.fetch_contacts", fetch_contacts_mock)

    results = [
        response async for response in fetch_contacts_pages_agen(httpx_client_mock)
    ]

    assert fetch_contacts_mock.call_count == 2
    assert results == fake_responses
