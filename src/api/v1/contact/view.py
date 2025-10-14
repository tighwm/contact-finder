from fastapi import APIRouter

router = APIRouter(
    prefix="/contact",
    tags=["Contact"],
)


@router.get("/q")
async def handle_query():
    pass
