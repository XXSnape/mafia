import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from general import settings
from general.log import configure_logging
from routers.game.users import router as game_users_router
from routers.game.groups import router as game_groups_router
from routers.settings import (
    ban_router,
    order_of_roles_router,
    common_router,
)


async def main() -> None:
    """
    Функция для запуска бота и задач по расписанию

    :return: None
    """
    configure_logging()
    scheduler = AsyncIOScheduler()
    scheduler.configure(timezone="Europe/Moscow")
    dp = Dispatcher(
        fsm_strategy=FSMStrategy.CHAT, scheduler=scheduler
    )
    dp.include_routers(
        game_groups_router,
        game_users_router,
        ban_router,
        order_of_roles_router,
        common_router,
    )
    commands = [
        BotCommand(
            command="registration", description="Запустить бота"
        ),
        BotCommand(
            command="settings",
            description="Персональные настройки игры",
        ),
    ]
    bot = Bot(
        token=settings.token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
