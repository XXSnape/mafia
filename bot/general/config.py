from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()
BASE_DIR = Path(__file__).parent.parent


class DBSettings(BaseSettings):
    echo: bool = True

    @property
    def url(self):
        return r"sqlite+aiosqlite:///D:\Users\КЕКС\PycharmProjects\mafia\db.sqlite3"


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
