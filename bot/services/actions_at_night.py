import asyncio
from pprint import pprint

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from cache.cache_types import GameCache, UserCache, UserIdInt
from constants.output import NUMBER_OF_NIGHT
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.roles import Hacker, Mafia
from services.roles.base import Role, ActiveRoleAtNight
from utils.tg import delete_message
from utils.utils import get_state_and_assign


def save_notification_message(
    game_data: GameCache,
    processed_user_id: int,
    message: str,
    current_user_id: int,
):
    if processed_user_id != current_user_id:
        game_data["messages_after_night"].append(
            [processed_user_id, message]
        )


def trace_all_actions(
    callback: CallbackQuery, game_data: GameCache, user_id: int
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


async def inform_aliases(
    current_role: Role,
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
        message = (
            NUMBER_OF_NIGHT.format(game_data["number_of_night"])
            + f"{pretty_role} {current_url} выбрал {url}"
        )
        await asyncio.gather(
            *(
                callback.bot.send_message(
                    chat_id=alias_id, text=message
                )
                for alias_id in game_data[current_role.roles_key]
                if alias_id != callback.from_user.id
            )
        )
        if callback.from_user.id in game_data[
            Mafia.roles_key
        ] and game_data.get(Hacker.roles_key):
            await asyncio.gather(
                *(
                    callback.bot.send_message(
                        chat_id=hacker_id,
                        text=f"{pretty_role} ??? выбрал {url}",
                    )
                    for hacker_id in game_data[Hacker.roles_key]
                )
            )


async def get_game_state_and_data(
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
    return game_state, game_data


async def get_game_state_data_and_user_id(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
) -> tuple[FSMContext, GameCache, UserIdInt]:
    game_state, game_data = await get_game_state_and_data(
        callback=callback, state=state, dispatcher=dispatcher
    )
    user_id = game_data["players_ids"][callback_data.user_index]
    return game_state, game_data, user_id


async def inform_players_and_trace_actions(
    callback: CallbackQuery,
    game_data: GameCache,
    user_id: int,
    current_role: ActiveRoleAtNight,
):
    url = game_data["players"][str(user_id)]["url"]
    await inform_aliases(
        current_role=current_role,
        game_data=game_data,
        callback=callback,
        url=url,
    )
    trace_all_actions(
        callback=callback, game_data=game_data, user_id=user_id
    )
    if (
        current_role.message_to_group_after_action
        and not game_data[current_role.processed_users_key]
    ):

        await callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text=current_role.message_to_group_after_action,
        )
    if current_role.message_to_user_after_action:
        await delete_message(callback.message)
        await callback.message.answer(
            NUMBER_OF_NIGHT.format(game_data["number_of_night"])
            + current_role.message_to_user_after_action.format(
                url=url
            )
        )
    if current_role.notification_message:
        save_notification_message(
            game_data=game_data,
            processed_user_id=user_id,
            message=current_role.notification_message,
            current_user_id=callback.from_user.id,
        )


async def take_action_and_register_user(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    game_state, game_data, user_id = (
        await get_game_state_data_and_user_id(
            callback=callback,
            callback_data=callback_data,
            state=state,
            dispatcher=dispatcher,
        )
    )
    enum_name = game_data["players"][str(callback.from_user.id)][
        "enum_name"
    ]
    current_role: ActiveRoleAtNight = get_data_with_roles(enum_name)
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

    if current_role.processed_users_key:
        game_data[current_role.processed_users_key].append(user_id)
    if (
        current_role.processed_by_boss
        and callback.from_user.id
        == game_data[current_role.roles_key][0]
    ):
        game_data[current_role.processed_by_boss].append(user_id)
    await state.set_data(game_data)
    return game_state, game_data, user_id
