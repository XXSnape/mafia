from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()
BASE_DIR = Path(__file__).parent.parent


class DBSettings(BaseSettings):
    @property
    def url(self):
        return "sqlite+aiosqlite:///./db.sqlite3"


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    token: str
    db: DBSettings = DBSettings()
    model_config = SettingsConfigDict(
        case_sensitive=False,
    )


settings = Settings()
