from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()
BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    token: str
    model_config = SettingsConfigDict(
        case_sensitive=False,
    )


settings = Settings()
