from contextlib import suppress

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from cache.cache_types import GameCache, UserCache, UserIdInt
from general.collection_of_roles import get_data_with_roles
from general.text import NUMBER_OF_NIGHT
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from mafia.roles import ActiveRoleAtNightABC, Hacker, Mafia
from utils.informing import send_a_lot_of_messages_safely
from utils.pretty_text import make_build
from utils.state import get_state_and_assign
from utils.tg import delete_message


async def send_messages_and_remove_from_expected(
    callback: CallbackQuery,
    game_data: GameCache,
    message_to_user: bool | str = True,
    message_to_group: bool | str = True,
    user_id: int | None = None,
    current_role: ActiveRoleAtNightABC | None = None,
    need_to_remove_from_expected: bool = True,
):
    if need_to_remove_from_expected:
        with suppress(ValueError):
            game_data["wait_for"].remove(callback.from_user.id)
    message_to_group_after_action = None
    if isinstance(message_to_group, str):
        message_to_group_after_action = message_to_group
    elif message_to_group is True:
        message_to_group_after_action = (
            current_role.message_to_group_after_action
        )
    if message_to_group_after_action:
        await callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text=make_build(message_to_group_after_action),
        )
    message_to_user_after_action = None
    if isinstance(message_to_user, str):
        message_to_user_after_action = message_to_user
    elif message_to_user is True:
        url = game_data["players"][str(user_id)]["url"]
        message_to_user_after_action = (
            current_role.message_to_user_after_action.format(url=url)
        )
    if message_to_user_after_action is not None:
        await callback.message.answer(
            make_build(
                NUMBER_OF_NIGHT.format(game_data["number_of_night"])
                + message_to_user_after_action
            )
        )


async def trace_all_actions(
    callback: CallbackQuery,
    game_data: GameCache,
    user_id: int,
    current_role: ActiveRoleAtNightABC,
    message_to_group: bool | str = True,
    message_to_user: bool | str = True,
    need_to_remove_from_expected: bool = True,
):
    suffer_tracking = game_data["tracking"].setdefault(
        str(callback.from_user.id), {}
    )
    sufferers = suffer_tracking.setdefault("sufferers", [])
    sufferers.append(user_id)

    interacting_tracking = game_data["tracking"].setdefault(
        str(user_id), {}
    )
    interacting = interacting_tracking.setdefault("interacting", [])
    interacting.append(callback.from_user.id)
    await send_messages_and_remove_from_expected(
        callback=callback,
        game_data=game_data,
        message_to_user=message_to_user,
        message_to_group=message_to_group,
        user_id=user_id,
        current_role=current_role,
        need_to_remove_from_expected=need_to_remove_from_expected,
    )


async def inform_aliases(
    current_role: ActiveRoleAtNightABC,
    game_data: GameCache,
    callback: CallbackQuery,
    url: str,
):
    if current_role.alias or current_role.is_alias:
        current_url = game_data["players"][
            str(callback.from_user.id)
        ]["url"]
        pretty_role = game_data["players"][
            str(callback.from_user.id)
        ]["pretty_role"]
        text = make_build(
            NUMBER_OF_NIGHT.format(game_data["number_of_night"])
            + f"{pretty_role} {current_url} выбрал {url}"
        )
        await send_a_lot_of_messages_safely(
            bot=callback.bot,
            users=game_data[current_role.roles_key],
            text=text,
            exclude=[callback.from_user.id],
        )
        if callback.from_user.id in game_data[
            Mafia.roles_key
        ] and game_data.get(Hacker.roles_key):
            await send_a_lot_of_messages_safely(
                bot=callback.bot,
                users=game_data[Hacker.roles_key],
                text=f"{pretty_role} ??? выбрал {url}",
            )


async def get_game_state_and_data(
    tg_obj: CallbackQuery | Message,
    state: FSMContext,
    dispatcher: Dispatcher,
) -> tuple[FSMContext, GameCache]:
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=tg_obj.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    return game_state, game_data


async def get_game_state_data_and_user_id(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
) -> tuple[FSMContext, GameCache, UserIdInt]:
    game_state, game_data = await get_game_state_and_data(
        tg_obj=callback, state=state, dispatcher=dispatcher
    )
    user_id = game_data["live_players_ids"][callback_data.user_index]
    return game_state, game_data, user_id


async def inform_players_and_trace_actions(
    callback: CallbackQuery,
    game_data: GameCache,
    user_id: int,
    current_role: ActiveRoleAtNightABC,
):
    url = game_data["players"][str(user_id)]["url"]
    await inform_aliases(
        current_role=current_role,
        game_data=game_data,
        callback=callback,
        url=url,
    )
    message_to_group = False
    if (
        current_role.message_to_group_after_action
        and len(game_data[current_role.processed_users_key]) == 1
    ):
        message_to_group = True

    await trace_all_actions(
        callback=callback,
        game_data=game_data,
        user_id=user_id,
        current_role=current_role,
        message_to_group=message_to_group,
    )


async def take_action_and_save_data(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    await delete_message(callback.message)
    game_state, game_data, user_id = (
        await get_game_state_data_and_user_id(
            callback=callback,
            callback_data=callback_data,
            state=state,
            dispatcher=dispatcher,
        )
    )
    role_id = game_data["players"][str(callback.from_user.id)][
        "role_id"
    ]
    current_role: ActiveRoleAtNightABC = get_data_with_roles(role_id)
    if current_role.processed_users_key:
        game_data[current_role.processed_users_key].append(user_id)
        if (
            current_role.is_alias
            or current_role.alias
            and current_role.alias.is_mass_mailing_list
        ):
            await game_state.set_data(game_data)
    await inform_players_and_trace_actions(
        callback=callback,
        game_data=game_data,
        user_id=user_id,
        current_role=current_role,
    )
    if current_role.last_interactive_key:
        current_night = game_data["number_of_night"]
        nights = game_data[
            current_role.last_interactive_key
        ].setdefault(str(user_id), [])
        if current_night not in nights:
            nights.append(current_night)
    if (
        current_role.processed_by_boss
        and callback.from_user.id
        == game_data[current_role.roles_key][0]
    ):
        game_data[current_role.processed_by_boss].append(user_id)
    await game_state.set_data(game_data)
    return game_state, game_data, user_id
