import asyncio

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from cache.cache_types import GameCache, UserCache
from constants.output import NUMBER_OF_NIGHT
from general.collection_of_roles import Roles
from keyboards.inline.cb.cb_text import (
    WEREWOLF_TO_DOCTOR_CB,
    WEREWOLF_TO_MAFIA_CB,
    WEREWOLF_TO_POLICEMAN_CB,
)
from services.actions_at_night import get_game_state_and_data
from services.roles import (
    Werewolf,
    Mafia,
    MafiaAlias,
    Doctor,
    DoctorAlias,
    Policeman,
    PolicemanAlias,
)
from states.states import UserFsm
from utils.utils import (
    get_profiles,
    get_state_and_assign,
    make_pretty,
)
from utils.validators import remind_commissioner_about_inspections

router = Router(name=__name__)


@router.callback_query(
    UserFsm.WEREWOLF_TURNS_INTO,
    F.data.in_(
        [
            WEREWOLF_TO_MAFIA_CB,
            WEREWOLF_TO_DOCTOR_CB,
            WEREWOLF_TO_POLICEMAN_CB,
        ]
    ),
)
async def werewolf_turns_into(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    data = {
        WEREWOLF_TO_MAFIA_CB: [
            [Mafia(), "don"],
            [MafiaAlias(), "mafia"],
        ],
        WEREWOLF_TO_DOCTOR_CB: [
            [Doctor(), "doctor"],
            [DoctorAlias(), "nurse"],
        ],
        WEREWOLF_TO_POLICEMAN_CB: [
            [Policeman(), "policeman"],
            [PolicemanAlias(), "general"],
        ],
    }
    game_state, game_data = await get_game_state_and_data(
        callback=callback, state=state, dispatcher=dispatcher
    )

    user_id = callback.from_user.id
    game_data[Werewolf.roles_key].remove(user_id)
    url = game_data["players"][str(user_id)]["url"]

    initial_role = game_data["players"][str(user_id)]["initial_role"]

    current_roles = data[callback.data]
    roles_key = current_roles[0][0].roles_key
    game_data[roles_key].append(callback.from_user.id)
    await callback.message.delete()
    are_there_many_senders = False
    if len(game_data[roles_key]) == 1:
        enum_name = current_roles[0][1]
        new_role = current_roles[0][0]
    else:
        enum_name = current_roles[1][1]
        new_role = current_roles[1][0]
        are_there_many_senders = True
    game_data["players"][str(user_id)]["role"] = new_role.role
    game_data["players"][str(user_id)]["pretty_role"] = make_pretty(
        new_role.role
    )
    game_data["players"][str(user_id)]["enum_name"] = enum_name
    game_data["players"][str(user_id)][
        "roles_key"
    ] = new_role.roles_key
    await game_state.set_data(game_data)
    await state.set_state(new_role.state_for_waiting_for_action)
    await callback.message.answer_photo(
        photo=new_role.photo,
        caption=f"Твоя новая роль - {make_pretty(new_role.role)}!",
    )
    await callback.bot.send_photo(
        chat_id=game_data["game_chat"],
        photo=new_role.photo,
        caption=f"{make_pretty(Werewolf.role)} принял решение превратиться в {make_pretty(new_role.role)}. "
        f"Уже со следующего дня изменения в миропорядке вступят в силу.",
    )
    if are_there_many_senders:
        profiles = get_profiles(
            players_ids=game_data[roles_key],
            players=game_data["players"],
            role=True,
        )
        await asyncio.gather(
            *(
                callback.bot.send_message(
                    chat_id=player_id,
                    text=NUMBER_OF_NIGHT.format(
                        game_data["number_of_night"]
                    )
                    + f"{initial_role} {url} превратился в {make_pretty(new_role.role)}\n"
                    f"Текущие союзники:\n{profiles}",
                )
                for player_id in game_data[roles_key]
            )
        )
    if callback.data == WEREWOLF_TO_POLICEMAN_CB:
        await callback.message.answer(
            text=remind_commissioner_about_inspections(game_data)
        )
