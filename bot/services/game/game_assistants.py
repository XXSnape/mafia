from contextlib import suppress

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from cache.cache_types import GameCache, UserCache, UserIdInt
from general.collection_of_roles import get_data_with_roles
from general.groupings import Groupings
from general.text import NUMBER_OF_NIGHT
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from mafia.roles import ActiveRoleAtNightABC, Hacker, Mafia
from utils.common import get_criminals_ids
from utils.informing import send_a_lot_of_messages_safely
from utils.pretty_text import make_build
from utils.state import get_state_and_assign, lock_state
from utils.tg import delete_message


def remove_from_expected(
    callback: CallbackQuery,
    game_data: GameCache,
    need_to_remove_from_expected: bool = True,
):
    if need_to_remove_from_expected:
        with suppress(ValueError):
            game_data["waiting_for_action_at_night"].remove(
                callback.from_user.id
            )


async def send_messages_to_user_and_group(
    callback: CallbackQuery,
    game_data: GameCache,
    message_to_user: bool | str = True,
    message_to_group: bool | str = True,
    user_id: UserIdInt | None = None,
    current_role: ActiveRoleAtNightABC | None = None,
):
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
            ),
            protect_content=game_data["settings"]["protect_content"],
        )


def trace_all_actions(
    callback: CallbackQuery,
    game_data: GameCache,
    user_id: UserIdInt,
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
    remove_from_expected(
        callback=callback,
        game_data=game_data,
        need_to_remove_from_expected=need_to_remove_from_expected,
    )


async def inform_aliases(
    current_role: ActiveRoleAtNightABC,
    game_data: GameCache,
    callback: CallbackQuery,
    url: str,
):
    if (
        (current_role.alias or current_role.is_alias)
        and game_data["settings"]["show_peaceful_allies"]
    ) or current_role.grouping == Groupings.criminals:
        current_url = game_data["players"][
            str(callback.from_user.id)
        ]["url"]
        pretty_role = game_data["players"][
            str(callback.from_user.id)
        ]["pretty_role"]
        text = make_build(
            NUMBER_OF_NIGHT.format(game_data["number_of_night"])
            + f"{pretty_role} {current_url} выбрал "
            f"{current_role.words_to_aliases_and_teammates.lower()} {url}"
        )
        users = game_data[current_role.roles_key]
        if current_role.grouping == Groupings.criminals:
            users = get_criminals_ids(game_data)

        await send_a_lot_of_messages_safely(
            bot=callback.bot,
            users=users,
            text=text,
            exclude=[callback.from_user.id],
            protect_content=game_data["settings"]["protect_content"],
        )
        if callback.from_user.id in game_data[
            Mafia.roles_key
        ] and game_data.get(Hacker.roles_key):
            await send_a_lot_of_messages_safely(
                bot=callback.bot,
                users=game_data[Hacker.roles_key],
                text=f"{pretty_role} ??? выбрал "
                f"{current_role.words_to_aliases_and_teammates.lower()} {url}",
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )


async def get_game_state_by_user_state(
    tg_obj: CallbackQuery | Message,
    user_state: FSMContext,
    dispatcher: Dispatcher,
    user_data: UserCache | None = None,
):
    if user_data is None:
        user_data: UserCache = await user_state.get_data()
    return await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=tg_obj.bot.id,
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


async def get_game_data_and_user_id(
    game_state: FSMContext,
    callback_data: UserActionIndexCbData,
) -> tuple[GameCache, UserIdInt]:
    game_data = await game_state.get_data()
    user_id = game_data["live_players_ids"][callback_data.user_index]
    return game_data, user_id


async def inform_players_after_action(
    callback: CallbackQuery,
    game_data: GameCache,
    user_id: UserIdInt,
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
        game_data["settings"]["show_roles_after_death"]
        and current_role.message_to_group_after_action
        and len(game_data[current_role.processed_users_key]) == 1
    ):
        message_to_group = True
    await send_messages_to_user_and_group(
        callback=callback,
        game_data=game_data,
        current_role=current_role,
        message_to_group=message_to_group,
        user_id=user_id,
    )


async def take_action_and_save_data(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
) -> tuple[FSMContext, UserIdInt] | tuple[None, None]:
    await delete_message(callback.message, raise_exception=True)
    game_state = await get_game_state_by_user_state(
        tg_obj=callback, dispatcher=dispatcher, user_state=state
    )
    async with lock_state(game_state):
        game_data, user_id = await get_game_data_and_user_id(
            game_state=game_state,
            callback_data=callback_data,
        )
        if (
            callback.from_user.id
            not in game_data["waiting_for_action_at_night"]
        ):
            return None, None
        role_id = game_data["players"][str(callback.from_user.id)][
            "role_id"
        ]
        current_role: ActiveRoleAtNightABC = get_data_with_roles(
            role_id
        )
        if current_role.processed_users_key:
            game_data[current_role.processed_users_key].append(
                user_id
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
        trace_all_actions(
            callback=callback,
            game_data=game_data,
            user_id=user_id,
        )
        await game_state.set_data(game_data)
    await inform_players_after_action(
        callback=callback,
        game_data=game_data,
        user_id=user_id,
        current_role=current_role,
    )
    return game_state, user_id
