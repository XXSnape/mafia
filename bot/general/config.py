from pathlib import Path

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from faststream.rabbit import RabbitBroker
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class AISettings(BaseSettings):
    deepseek_api_key: str
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    md_path: Path = base_dir / "docs" / "detailed-readme.md"
    faiss_path: Path = base_dir / "faiss_db"
    max_chunk_size: int = 512
    chunk_overlap: int = 50
    lm_model_name: str = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    base_url: str = "https://openrouter.ai/api/v1"
    deepseek_model_name: str = "deepseek/deepseek-r1-0528:free"
    unavailable_message: str = (
        "😢Извините, Mafia AI временно не работает"
    )
    use: bool
    model_config = SettingsConfigDict(
        case_sensitive=False, env_prefix="ai_"
    )


class RabbitSettings(BaseSettings):
    default_user: str
    default_pass: str
    host: str
    port: int

    model_config = SettingsConfigDict(
        case_sensitive=False, env_prefix="rabbitmq_"
    )

    @property
    def url(self):
        return (
            f"amqp://{self.default_user}:"
            f"{self.default_pass}@{self.host}:{self.port}/"
        )


class RedisSettings(BaseSettings):
    host: str
    port: int

    model_config = SettingsConfigDict(
        case_sensitive=False, env_prefix="redis_"
    )


class BotSettings(BaseSettings):
    token: str
    url: str
    model_config = SettingsConfigDict(
        case_sensitive=False, env_prefix="bot_"
    )


class MafiaSettings(BaseSettings):
    maximum_number_of_players: int
    minimum_number_of_players: int
    maximum_registration_time: int
    init_db: bool
    number_of_characters_in_message: int = 4064
    time_for_night: int = 45
    time_for_day: int = 45
    time_for_voting: int = 35
    time_for_confirmation: int = 35
    model_config = SettingsConfigDict(
        case_sensitive=False, env_prefix="mafia_"
    )


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

    ai: AISettings = AISettings()
    rabbit: RabbitSettings = RabbitSettings()
    db: DBSettings = DBSettings()
    bot: BotSettings = BotSettings()
    mafia: MafiaSettings = MafiaSettings()
    redis: RedisSettings = RedisSettings()
    model_config = SettingsConfigDict(
        case_sensitive=False,
    )


settings = Settings()
broker = RabbitBroker(settings.rabbit.url)
bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(parse_mode="HTML"),
)
