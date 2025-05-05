from fastapi import APIRouter
from .user_test import router as user_router

router = APIRouter()

router.include_router(router=user_router, prefix="/user")

__all__ = ["router"]