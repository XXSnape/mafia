from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext

from cache.cache_types import GameCache
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from services.registartion import get_state_and_assign
from states.states import UserFsm


async def familiarize_players(bot: Bot, state: FSMContext):
    game_data: GameCache = await state.get_data()
    mafias = game_data["mafias"]
    doctors = game_data["doctors"]
    policeman = game_data["policeman"]
    civilians = game_data["civilians"]

    for user_id in mafias:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - Мафия! Тебе нужно уничтожить всех горожан.",
        )
    for user_id in doctors:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - Доктор! Тебе нужно стараться лечить тех, кому нужна помощь.",
        )
    for user_id in policeman:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - Комиссар! Тебе нужно вычислить мафию.",
        )
    for user_id in civilians:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - Мирный житель! Тебе нужно вычислить мафию на голосовании.",
        )


async def mail_mafia(
    dispatcher: Dispatcher,
    bot: Bot,
    state: FSMContext,
):
    game_data: GameCache = await state.get_data()
    mafias = game_data["mafias"]
    mafia_id = mafias[0]
    players = game_data["players"]
    markup = send_selection_to_players_kb(
        players_ids=game_data["players_ids"],
        players=players,
        exclude=mafia_id,
    )

    sent_survey = await bot.send_message(
        chat_id=mafia_id,
        text="Кого убить этой ночью?",
        reply_markup=markup,
    )
    game_data["to_delete"].append(sent_survey.message_id)

    await state.set_data(game_data)
    await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=mafia_id,
        bot_id=bot.id,
        new_state=UserFsm.MAFIA_ATTACKS,
    )


async def main_doctor(
    dispatcher: Dispatcher,
    bot: Bot,
    state: FSMContext,
):
    game_data: GameCache = await state.get_data()
    doctors = game_data["doctors"]
    doctor_id = doctors[0]
    players = game_data["players"]
    exclude = (
        []
        if game_data["last_treated"] == 0
        else game_data["last_treated"]
    )
    markup = send_selection_to_players_kb(
        players_ids=game_data["players_ids"],
        players=players,
        exclude=exclude,
    )
    sent_survey = await bot.send_message(
        chat_id=doctor_id,
        text="Кого вылечить этой ночью?",
        reply_markup=markup,
    )
    game_data["to_delete"].append(sent_survey.message_id)
    await state.set_data(game_data)
    await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=doctor_id,
        bot_id=bot.id,
        new_state=UserFsm.DOCTOR_TREATS,
    )
