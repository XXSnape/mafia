from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from constants.output import NUMBER_OF_NIGHT
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import PLAYER_BACKS_CB
from keyboards.inline.keypads.mailing import choose_fake_role_kb
from services.actions_at_night import (
    get_game_state_data_and_user_id,
    get_game_state_and_data,
    trace_all_actions,
    save_notification_message,
)
from services.roles import Forger, Policeman, PolicemanAlias
from states.states import UserFsm
from utils.utils import make_pretty

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
    _, game_data, user_id = await get_game_state_data_and_user_id(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
    )

    url = game_data["players"][str(user_id)]["url"]
    game_data["forged_roles"].append([user_id])
    all_roles = get_data_with_roles()
    current_roles = [
        (all_roles[data["enum_name"]].role, data["enum_name"])
        for _, data in game_data["players"].items()
        if data["role"] not in (Policeman.role, PolicemanAlias.role)
    ]
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
    _, game_data = await get_game_state_and_data(
        callback=callback, state=state, dispatcher=dispatcher
    )
    game_data["forged_roles"].clear()
    markup = Forger().generate_markup(
        player_id=callback.from_user.id, game_data=game_data
    )
    await callback.message.edit_text(
        text=Forger.mail_message,
        reply_markup=markup,
    )


@router.callback_query(UserFsm.FORGER_FAKES, F.data)
async def forges_selects_documents(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    _, game_data = await get_game_state_and_data(
        callback=callback, state=state, dispatcher=dispatcher
    )
    current_role = get_data_with_roles(callback.data)
    pretty_role = make_pretty(current_role.role)
    game_data["forged_roles"][0].append(pretty_role)
    user_id = game_data["forged_roles"][0][0]
    trace_all_actions(
        callback=callback, game_data=game_data, user_id=user_id
    )
    save_notification_message(
        game_data=game_data,
        processed_user_id=user_id,
        message=Forger.notification_message,
        current_user_id=callback.from_user.id,
    )
    url = game_data["players"][str(user_id)]["url"]
    await callback.message.delete()
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text=Forger.message_to_group_after_action,
    )
    await callback.message.answer(
        text=NUMBER_OF_NIGHT.format(game_data["number_of_night"])
        + f"Ты выбрал подменить документы {url} на {pretty_role}"
    )
