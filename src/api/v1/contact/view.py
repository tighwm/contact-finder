from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.contact.crud import get_contacts_by_query
from api.v1.contact.schema import ContactSchema
from core.models import db_helper

router = APIRouter(
    prefix="/contact",
    tags=["Contact"],
)


@router.get("/{q}", response_model=list[ContactSchema])
async def handle_query(
    q: str,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    result = await get_contacts_by_query(session=session, query=q)
    return [ContactSchema.model_validate(contact, by_name=True) for contact in result]
