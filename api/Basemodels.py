from pydantic import BaseModel


class UserPassportResponse(BaseModel):
    id: int
    name: str
    faculty: str
    telegram_id: str
    passport: str

