from pathlib import Path

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from faststream.rabbit import RabbitBroker
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()
BASE_DIR = Path(__file__).parent.parent


class RabbitSettings(BaseSettings):
    @property
    def url(self):
        return "amqp://guest:guest@localhost:5672/"


class DBSettings(BaseSettings):
    echo: bool = True

    @property
    def url(self):
        return r"sqlite+aiosqlite:////home/nachi/PycharmProjects/mafia/db.sqlite3"


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    token: str
    rabbit: RabbitSettings = RabbitSettings()
    db: DBSettings = DBSettings()
    model_config = SettingsConfigDict(
        case_sensitive=False,
    )


settings = Settings()
broker = RabbitBroker(settings.rabbit.url)
bot = Bot(
    token=settings.token,
    default=DefaultBotProperties(parse_mode="HTML"),
)
