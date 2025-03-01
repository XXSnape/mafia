from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext

from cache.cache_types import GameCache
from keyboards.inline.keypads.to_bot import get_to_bot_kb
from services.registartion import select_roles
from services.mailing import mail_mafia, main_doctor

from states.states import GameFsm


async def start_night(
    bot: Bot, dispatcher: Dispatcher, state: FSMContext, chat_id: int
):
    game_data: GameCache = await state.get_data()
    game_data["number_of_night"] += 1
    await state.set_data(game_data)
    await bot.send_message(
        chat_id=chat_id,
        text=f"Наступает ночь {game_data['number_of_night']}.\n\nВсем приготовиться.",
        reply_markup=get_to_bot_kb("Действовать!"),
    )
    if game_data["mafias"]:
        await mail_mafia(dispatcher=dispatcher, bot=bot, state=state)
    if game_data["doctors"]:
        await main_doctor(
            dispatcher=dispatcher, bot=bot, state=state
        )


async def start_game(
    chat_id: int,
    message_id: int,
    bot: Bot,
    state: FSMContext,
):
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )
    await state.set_state(GameFsm.STARTED)
    await bot.send_message(
        chat_id=chat_id,
        text="Игра начинается!",
        reply_markup=get_to_bot_kb(),
    )
    await select_roles(state=state, bot=bot)
