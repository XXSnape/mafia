from aiogram import Router, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.cache_types import UserCache, GameCache
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
    UserVoteIndexCbData,
)
from keyboards.inline.keypads.to_bot import (
    participate_in_social_life,
)
from services.registartion import get_state_and_assign
from states.states import UserFsm

router = Router()


@router.callback_query(
    UserFsm.MAFIA_ATTACKS, UserActionIndexCbData.filter()
)
async def mafia_attacks(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=callback.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    await callback.bot.send_message(
        chat_id=user_data["game_chat"], text="Мафия выбрала жертву!"
    )
    died_user_id = game_data["players_ids"][callback_data.user_index]
    game_data["died"].append(died_user_id)
    url = game_data["players"][str(died_user_id)]["url"]
    await callback.message.edit_text(f"Ты выбрал убить {url}")
    game_data["to_delete"].remove(callback.message.message_id)


@router.callback_query(
    UserFsm.DOCTOR_TREATS, UserActionIndexCbData.filter()
)
async def doctor_treats(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=callback.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    await callback.bot.send_message(
        chat_id=user_data["game_chat"],
        text="Доктор спешит кому-то на помощь!",
    )
    recovered_user_id = game_data["players_ids"][
        callback_data.user_index
    ]
    game_data["recovered"].append(recovered_user_id)
    url = game_data["players"][str(recovered_user_id)]["url"]
    game_data["last_treated"] = recovered_user_id
    await callback.message.edit_text(f"Ты выбрал вылечить {url}")
    game_data["to_delete"].remove(callback.message.message_id)
    await game_state.set_data(game_data)


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS, UserActionIndexCbData.filter()
)
async def policeman_checks(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=callback.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    await callback.bot.send_message(
        chat_id=user_data["game_chat"],
        text="РАБОТАЕТ местная полиция!",
    )
    checked_user_id = game_data["players_ids"][
        callback_data.user_index
    ]
    role = game_data["players"][str(checked_user_id)]["role"]
    url = game_data["players"][str(checked_user_id)]["url"]
    await callback.message.edit_text(f"{url} - {role}!")
    game_data["to_delete"].remove(callback.message.message_id)


@router.callback_query(UserVoteIndexCbData.filter())
async def vote_for(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=callback.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    voted_user_id = game_data["players_ids"][
        callback_data.user_index
    ]
    game_data["vote_for"].append(voted_user_id)
    voting_url = game_data["players"][str(callback.from_user.id)][
        "url"
    ]
    voted_url = game_data["players"][str(voted_user_id)]["url"]
    await callback.message.edit_text(
        f"Ты выбрал голосовать за {voted_url}"
    )
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text=f"{voting_url} выступает против {voted_url}!",
        reply_markup=participate_in_social_life(),
    )
