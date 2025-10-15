import logging
from typing import Annotated, Any, AsyncGenerator

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends

from core import broker
from core.models import db_helper
from api.v1.contact.schema import NimbleResponse
from api.v1.contact.crud import batch_insert_contacts
from tasks.depends import get_httpx_client
from tenacity import retry, wait_random_exponential, stop_after_attempt

log = logging.getLogger(__name__)

NIMBLE_CONTACTS_ENDPOINT = "/contacts"


def extract_contacts_from_responses_as_dicts(
    response: NimbleResponse,
) -> list[dict[str, Any]]:
    """Extracting contacts as dicts from NimbleResponse object for inserting to db"""
    return [
        {
            "nimble_id": resource.id,
            "first_name": resource.fields.first_name[0].value,
            "last_name": resource.fields.last_name[0].value,
            "email": resource.fields.email[0].value,
            "description": resource.fields.description[0].value,
        }
        for resource in response.resources
    ]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def fetch_contacts(
    client: httpx.AsyncClient,
    page: int = 1,
    per_page: int = 50,
    fields: str = "first name,last name,email,description",
    record_type: str = "person",
) -> NimbleResponse:
    params = {
        "record_type": record_type,
        "fields": fields,
        "page": page,
        "per_page": per_page,
    }
    http_response = await client.get(
        url=NIMBLE_CONTACTS_ENDPOINT,
        params=params,
    )
    http_response.raise_for_status()
    response = NimbleResponse.model_validate(
        http_response.json(),
        extra="ignore",
    )
    return response


async def fetch_contacts_pages_agen(
    client: httpx.AsyncClient,
) -> AsyncGenerator[NimbleResponse, None]:
    """AsyncGenerator that yielding responses from Nimble API"""
    try:
        response = await fetch_contacts(client)
    except httpx.HTTPStatusError as e:
        log.error(
            "Error `%s` after trying request Nimble API `%s` endpoint with status code %s",
            e,
            NIMBLE_CONTACTS_ENDPOINT,
            e.response.status_code,
        )
        return

    yield response
    pages = response.meta.pages
    if pages > 1:
        for page_n in range(2, pages + 1):
            response = await fetch_contacts(
                client=client,
                page=page_n,
            )
            yield response


@broker.task(schedule=[{"cron": "0 * * * *"}])
async def update_contacts_per_day(
    client: Annotated[httpx.AsyncClient, TaskiqDepends(get_httpx_client)],
    session: Annotated[
        AsyncSession,
        TaskiqDepends(db_helper.session_getter),
    ],
) -> None:
    async for response in fetch_contacts_pages_agen(client):
        contacts = extract_contacts_from_responses_as_dicts(response)
        result = await batch_insert_contacts(
            session=session,
            contacts=contacts,
            on_conflict_do_update_index_elements=["nimble_id"],
        )
        log.info("Inserted/updated contacts: %d", len(result))
