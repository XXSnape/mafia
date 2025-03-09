import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.strategy import FSMStrategy
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from general import settings
from general.log import configure_logging
from routers.groups import router as groups_router
from routers.users import router as user_router


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
    dp.include_routers(groups_router, user_router)
    bot = Bot(
        token=settings.token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
