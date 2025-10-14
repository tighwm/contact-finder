import csv
import logging

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Contact

log = logging.getLogger(__name__)


class ContactCsv(BaseModel):
    first_name: str = Field(alias="first name")
    last_name: str = Field(alias="last name")
    email: str
    description: str


async def import_csv_if_not_exists(session: AsyncSession):
    contacts = []
    with open("NimbleContacts.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                contact_schema = ContactCsv.model_validate(row)
            except ValidationError:
                continue
            contacts.append(contact_schema.model_dump())
    if not contacts:
        log.info("No contacts to import from csv.")
        return

    stmt = (
        insert(Contact)
        .values(contacts)
        .on_conflict_do_nothing(index_elements=["email"])
        .returning(Contact.id)
    )
    result = await session.execute(stmt)
    await session.commit()
    log.info("Imported from csv to Contacts table: %s", result.scalars().all())
