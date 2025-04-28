from fastapi import APIRouter, Depends, HTTPException, status
from utils import DatabaseService, get_db_core
from typing import List
from data import engine

db = DatabaseService(engine=engine)

router = APIRouter(
    prefix="/api",
    tags=["Teachers"],
    dependencies=[Depends(get_db_core)],
    responses={404: {"description": "Not found"}},
)

@router.get("/teachers/", response_model=List[dict])
async def read_teachers(db: DatabaseService = Depends(get_db_core)):
    try:
        return db.get_teachers()