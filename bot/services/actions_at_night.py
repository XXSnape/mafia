from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.cache_types import (
    UserCache,
    GameCache,
    Roles,
    Role,
)
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from utils.utils import get_state_and_assign


async def get_user_id_and_inform_players(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
    role: Roles,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=callback.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    current_role: Role = role.value
    if current_role.message_to_group_after_action:
        await callback.bot.send_message(
            chat_id=user_data["game_chat"],
            text=current_role.message_to_group_after_action,
        )
    user_id = game_data["players_ids"][callback_data.user_index]
    url = game_data["players"][str(user_id)]["url"]

    if (
        game_data.get("tracking") is not None
        and role != Roles.journalist
    ):

        suffer_tracking = game_data["tracking"].setdefault(
            str(callback.from_user.id), {}
        )
        sufferers = suffer_tracking.setdefault("sufferers", [])
        sufferers.append(user_id)

        interacting_tracking = game_data["tracking"].setdefault(
            str(user_id), {}
        )
        interacting = interacting_tracking.setdefault(
            "interacting", []
        )
        interacting.append(callback.from_user.id)

    if current_role.message_to_user_after_action:
        await callback.message.delete()
        await callback.message.answer(
            current_role.message_to_user_after_action.format(url=url)
        )
    return game_state, game_data, user_id


async def take_action_and_register_user(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
    role: Roles,
):
    current_role: Role = role.value
    game_state, game_data, user_id = (
        await get_user_id_and_inform_players(
            callback=callback,
            callback_data=callback_data,
            state=state,
            dispatcher=dispatcher,
            role=role,
        )
    )
    if current_role.last_interactive_key:
        game_data[current_role.last_interactive_key][:] = [user_id]
    if current_role.processed_users_key:
        game_data[current_role.processed_users_key].append(user_id)
    return game_data, user_id
