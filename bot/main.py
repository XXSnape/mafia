import asyncio
import orjson

from aiogram import Dispatcher
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from general.config import bot, broker
from general.log import configure_logging
from routers.game.users import router as game_users_router
from aiogram.fsm.storage.redis import RedisStorage
from routers.game.groups import router as game_groups_router
from routers.users import router as users_router
from routers.groups import router as groups_router


# from routers.groups.adding import router as adding_router
# from routers.users.start import router as start_router
# from routers.groups.settings import router as groups_settings_router

from redis.asyncio import Redis


async def main() -> None:
    """
    Функция для запуска бота и задач по расписанию

    :return: None
    """
    configure_logging()
    scheduler = AsyncIOScheduler()
    scheduler.configure(timezone="Europe/Moscow")
    redis = Redis(host="localhost")
    storage = RedisStorage(redis=redis, json_loads=orjson.loads)
    dp = Dispatcher(
        fsm_strategy=FSMStrategy.CHAT,
        scheduler=scheduler,
        broker=broker,
        storage=storage,
    )
    dp.include_routers(
        game_groups_router,
        game_users_router,
        users_router,
        groups_router,
    )
    commands = [
        BotCommand(
            command="registration", description="Запустить бота"
        ),
        BotCommand(
            command="my_settings",
            description="Персональные настройки игры",
        ),
        BotCommand(
            command="settings",
            description="Общие настройки игры",
        ),
        BotCommand(
            command="extend", description="Продлить регистрацию"
        ),
        BotCommand(
            command="revoke", description="Отменить регистрацию"
        ),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
    scheduler.start()
    await broker.connect()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
