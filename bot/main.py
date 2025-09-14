import asyncio

import orjson
from ai.configure import configure_ai
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.common.sessions import engine
from database.dao.init_db import fill_database_with_roles
from general import settings
from general.config import bot, broker
from general.launch import launch
from general.log import configure_logging
from loguru import logger
from redis.asyncio import Redis


def json_dumps[**P](*args: P.args, **kwargs: P.kwargs) -> str:
    return orjson.dumps(*args, **kwargs).decode()


async def main() -> None:
    """
    Функция для запуска бота

    :return: None
    """
    configure_logging()
    await fill_database_with_roles()
    scheduler = AsyncIOScheduler()
    scheduler.configure()
    redis = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
    )
    storage = RedisStorage(
        redis=redis,
        json_loads=orjson.loads,
        json_dumps=json_dumps,
    )
    ai = configure_ai()
    dp = Dispatcher(
        fsm_strategy=FSMStrategy.CHAT,
        scheduler=scheduler,
        broker=broker,
        storage=storage,
        ai=ai,
    )
    try:
        logger.info("Запускаем мафию...")
        await launch(dp=dp)
        scheduler.start()
        await broker.connect()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Мафия остановлена!")
    finally:
        logger.info(
            "Начинается процесс остановки мафии и освобождения ресурсов..."
        )
        await broker.close()
        await engine.dispose()
        await redis.aclose()
        try:
            scheduler.shutdown(wait=False)
        except AttributeError:
            logger.warning("Планировщик не был запущен.")
        logger.success("Ресурсы для мафии успешно освобождены!")


if __name__ == "__main__":
    asyncio.run(main())
