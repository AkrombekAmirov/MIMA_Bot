from fastapi import APIRouter, Depends, HTTPException, status
from utils import DatabaseService
from typing import List
from data import engine

db = DatabaseService(engine=engine)

router = APIRouter(
    prefix="/api",
    tags=["Teachers"],
    responses={404: {"description": "Not found"}},
)

@router.get("/teachers/", response_model=List[dict])
async def read_teachers(db: DatabaseService = Depends()):
    try:
        return db.get_teachers()