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
from general.commands import BotCommands
from general.config import bot, broker
from general.log import configure_logging
from middlewares.errors import (
    HandleCallbackErrorMiddleware,
    HandleMessageErrorMiddleware,
)
from redis.asyncio import Redis
from routers.game.groups import router as game_groups_router
from routers.game.users import router as game_users_router
from routers.groups import router as groups_router
from routers.users import (
    always_available_router,
)
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
        game_groups_router,
        game_users_router,
        users_router,
        groups_router,
    )
    private_commands = [
        BotCommand(
            command=BotCommands.help.name,
            description=BotCommands.help,
        ),
        BotCommand(
            command=BotCommands.my_settings.name,
            description=BotCommands.my_settings,
        ),
        BotCommand(
            command=BotCommands.profile.name,
            description=BotCommands.profile,
        ),
        BotCommand(
            command=BotCommands.shop.name,
            description=BotCommands.shop,
        ),
    ]
    group_commands = [
        BotCommand(
            command=BotCommands.registration.name,
            description=BotCommands.registration,
        ),
        BotCommand(
            command=BotCommands.game.name,
            description=BotCommands.game,
        ),
        BotCommand(
            command=BotCommands.extend.name,
            description=BotCommands.extend,
        ),
        BotCommand(
            command=BotCommands.revoke.name,
            description=BotCommands.revoke,
        ),
        BotCommand(
            command=BotCommands.leave.name,
            description=BotCommands.leave,
        ),
        BotCommand(
            command=BotCommands.settings.name,
            description=BotCommands.settings,
        ),
        BotCommand(
            command=BotCommands.statistics.name,
            description=BotCommands.statistics,
        ),
        BotCommand(
            command=BotCommands.subscribe.name,
            description=BotCommands.subscribe,
        ),
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
