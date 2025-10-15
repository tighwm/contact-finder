from fastapi import APIRouter
from api.v1.contact.view import router as contact_router

router = APIRouter(prefix="/v1")
router.include_router(contact_router)
