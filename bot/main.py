import asyncio

import orjson
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.dao.init_db import fill_database_with_roles
from general import settings
from general.commands import PrivateCommands, GroupCommands
from general.config import bot, broker
from general.log import configure_logging
from middlewares.errors import (
    HandleCallbackErrorMiddleware,
    HandleMessageErrorMiddleware,
)
from redis.asyncio import Redis

from routers.game import router as game_router

from routers.groups import router as groups_router
from routers import always_available_router
from routers.users import router as users_router


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
    redis = Redis(host=settings.redis.host, port=settings.redis.port)
    storage = RedisStorage(
        redis=redis, json_loads=orjson.loads, json_dumps=json_dumps
    )
    dp = Dispatcher(
        fsm_strategy=FSMStrategy.CHAT,
        scheduler=scheduler,
        broker=broker,
        storage=storage,
    )
    dp.callback_query.middleware(HandleCallbackErrorMiddleware())
    dp.message.middleware(HandleMessageErrorMiddleware())
    dp.include_routers(
        always_available_router,
        game_router,
        users_router,
        groups_router,
    )
    private_commands = [
        BotCommand(command=command.name, description=command)
        for command in PrivateCommands
    ]

    group_commands = [
        BotCommand(command=command.name, description=command)
        for command in GroupCommands
    ]
    await bot.set_my_commands(
        private_commands, BotCommandScopeAllPrivateChats()
    )
    await bot.set_my_commands(
        group_commands, BotCommandScopeAllGroupChats()
    )
    scheduler.start()
    await broker.connect()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
