from aiogram import Bot
from aiogram.fsm.context import FSMContext

from utils.play import select_roles

from states.states import GameFsm


async def start_first_night(
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
    await bot.send_message(chat_id=chat_id, text="Игра начинается!")
    await select_roles(state=state)
