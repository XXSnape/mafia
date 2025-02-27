import logging
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

def configure_logging(level=logging.INFO) -> None:
    """
    Конфигурирует настройки логирования

    :param level: Уровень логирования
    :return: None
    """
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
    )

settings = Settings()