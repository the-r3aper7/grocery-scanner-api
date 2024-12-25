from fastapi import APIRouter

from app.api.v1.endpoints import search

router = APIRouter()

router.include_router(search.router, prefix="/search", tags=["search"])
