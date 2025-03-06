from aiogram import Router, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.cache_types import (
    UserCache,
    GameCache,
    Roles,
    AliasesRole,
)
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import (
    PLAYER_BACKS_CB,
)
from keyboards.inline.keypads.mailing import (
    choose_fake_role_kb,
)

from services.mailing import MailerToPlayers
from states.states import UserFsm
from utils.utils import get_state_and_assign, make_pretty

router = Router(name=__name__)


@router.callback_query(
    UserFsm.FORGER_FAKES, UserActionIndexCbData.filter()
)
async def forger_fakes(
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
    user_id = game_data["players_ids"][callback_data.user_index]
    url = game_data["players"][str(user_id)]["url"]
    game_data: GameCache = await game_state.get_data()
    game_data["forged_roles"].append([user_id])
    current_roles = [
        Roles[data["enum_name"]]
        # data["role"]
        for _, data in game_data["players"].items()
        if data["role"]
        not in (
            Roles.policeman.value.role,
            AliasesRole.general.value.role,
        )
    ]

    await state.set_data(game_data)
    markup = choose_fake_role_kb(current_roles)
    await callback.message.edit_text(
        text=f"Выбери для {url} новую роль", reply_markup=markup
    )


@router.callback_query(
    UserFsm.FORGER_FAKES, F.data == PLAYER_BACKS_CB
)
async def forges_cancels_selection(
    callback: CallbackQuery,
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
    game_data["forged_roles"].clear()
    markup = MailerToPlayers.generate_markup(
        player_id=callback.from_user.id,
        current_role=Roles.forger.value,
        game_data=game_data,
    )
    await callback.message.edit_text(
        text=Roles.forger.value.interactive_with.mail_message,
        reply_markup=markup,
    )


@router.callback_query(UserFsm.FORGER_FAKES, F.data)
async def forges_selects_documents(
    callback: CallbackQuery,
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
    current_enum = Roles[callback.data]
    game_data["forged_roles"][0].append(
        make_pretty(current_enum.value.role)
    )
    user_id = game_data["forged_roles"][0][0]
    game_data["tracking"][str(callback.from_user.id)] = {
        "sufferers": [user_id]
    }
    url = game_data["players"][str(user_id)]["url"]
    await callback.message.delete()
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text=Roles.forger.value.message_to_group_after_action,
    )
    await callback.message.answer(
        text=f"Ты выбрал подменить документы {url} на {make_pretty(current_enum.value.role)}"
    )
