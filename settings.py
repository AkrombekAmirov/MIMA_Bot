# settings.py

from pathlib import Path
from typing import List, Union, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )

    # ⚙️ Endi APP_NAME ham bor
    APP_NAME: str = Field("MIMA Bot", description="Ilova nomi")
    DEBUG: bool = False

    BOT_TOKEN: str
    DATABASE_URL: str
    SESSION_SECRET: str

    IP: str
    ENV: str

    ADMIN_M1: int
    ADMIN_M2: int
    ADMINS: List[int] = Field(default_factory=list)

    CORS_ORIGINS: Union[List[str], str] = Field(default_factory=list)

    BASE_DIR: Path = Path(__file__).parent
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    @field_validator("ADMINS", mode="before")
    @classmethod
    def _normalize_admins(cls, v: Any) -> List[int]:
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip().isdigit()]
        if isinstance(v, list):
            return [int(x) for x in v if isinstance(x, (int, str)) and str(x).isdigit()]
        return []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _normalize_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [h.strip() for h in v.split(",") if h.strip()]
        if isinstance(v, list):
            return [str(h) for h in v if isinstance(h, str) and h.strip()]
        return []

settings = Settings()
