from aiogram import Router, Dispatcher, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from cache.cache_types import (
    Roles,
    UserCache,
    GameCache,
)
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.actions_at_night import (
    get_user_id_and_inform_players,
    take_action_and_register_user,
)
from states.states import UserFsm
from utils.utils import get_state_and_assign

router = Router(name=__name__)


@router.callback_query(
    UserFsm.MAFIA_ATTACKS, UserActionIndexCbData.filter()
)
async def mafia_attacks(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    await take_action_and_register_user(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
        role=Roles.don.value.alias.role,
    )


@router.callback_query(
    UserFsm.DON_ATTACKS, UserActionIndexCbData.filter()
)
async def don_attacks(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):

    game_data, user_id = await take_action_and_register_user(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
        role=Roles.don,
    )
    game_data["killed_by_don"].append(user_id)


@router.message(
    StateFilter(UserFsm.DON_ATTACKS, UserFsm.MAFIA_ATTACKS), F.text
)
async def mafia_communicate(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=message.bot.id,
    )

    game_data: GameCache = await game_state.get_data()
    url = game_data["players"][str(message.from_user.id)]["url"]
    role = game_data["players"][str(message.from_user.id)][
        "pretty_role"
    ]
    for mafia_id in game_data["mafias"]:
        if mafia_id != message.from_user.id:
            await message.bot.send_message(
                chat_id=mafia_id,
                text=f"{role} {url} передает:\n{message.text}",
            )
    if len(game_data["mafias"]) > 1:
        await message.answer("Сообщение успешно отправлено!")
