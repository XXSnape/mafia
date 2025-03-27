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
    """
    db_host: хост базы
    db_port: порт базы
    postgres_user: логин пользователя
    postgres_password: пароль пользователя
    postgres_db: название базы
    echo: bool = True, если нужно, чтобы запросы выводились в консоль, иначе False
    """

    db_host: str
    db_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    echo: bool = False

    @property
    def url(self) -> str:
        """
        Возвращает строку для подключения к базе данных.
        """
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.db_host}:{self.db_port}/{self.postgres_db}"
        )


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
