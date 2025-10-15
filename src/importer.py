import asyncio
import csv
import logging
from typing import Any

from pydantic import ValidationError

from api.v1.contact.crud import batch_insert_contacts
from api.v1.contact.schema import ContactBase
from core.config import settings
from core.models import db_helper

logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
    datefmt=settings.logging.date_format,
)

log = logging.getLogger(__name__)


def read_csv() -> list[dict[str, Any]]:
    contacts = []
    with open("NimbleContacts.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                contact_schema = ContactBase.model_validate(row)
            except ValidationError:
                continue
            contacts.append(contact_schema.model_dump())
    return contacts


async def main():
    session = db_helper.local_session()
    contacts = read_csv()
    result = await batch_insert_contacts(session, contacts)
    log.info(
        "Imported from csv to Contacts table: %s",
        result,
    )
    await session.commit()
    await session.aclose()
    await db_helper.dispose()


if __name__ == "__main__":
    asyncio.run(main())
