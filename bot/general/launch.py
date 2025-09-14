from aiogram import Dispatcher
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)
from general.commands import GroupCommands, PrivateCommands
from general.config import bot
from middlewares.errors import (
    HandleCallbackErrorMiddleware,
    HandleMessageErrorMiddleware,
)
from routers import always_available_router
from routers.game import router as game_router
from routers.groups import router as groups_router
from routers.users import router as users_router


async def launch(dp: Dispatcher) -> None:
    dp.callback_query.middleware(HandleCallbackErrorMiddleware())
    dp.message.middleware(HandleMessageErrorMiddleware())
    dp.include_routers(
        always_available_router,
        groups_router,
        game_router,
        users_router,
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
