import asyncio

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.cache_types import GameCache, UserCache
from general.collection_of_roles import Roles

from keyboards.inline.callback_factory.recognize_user import (
    CheckOrKill,
    PoliceActionIndexCbData,
    police_check_cb_data,
    police_kill_cb_data,
)
from keyboards.inline.cb.cb_text import (
    PLAYER_BACKS_CB,
    POLICEMAN_CHECKS_CB,
    POLICEMAN_KILLS_CB,
)
from keyboards.inline.keypads.mailing import (
    POLICEMAN_BACK_BTN,
    send_selection_to_players_kb,
    kill_or_check_on_policeman,
)
from services.actions_at_night import (
    take_action_and_register_user,
)
from services.roles import Policeman
from states.states import UserFsm
from utils.utils import get_state_and_assign

router = Router(name=__name__)


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS,
    F.data.in_([POLICEMAN_KILLS_CB, POLICEMAN_CHECKS_CB]),
)
async def policeman_makes_choice(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    data = {
        POLICEMAN_KILLS_CB: [
            police_kill_cb_data,
            "Кого будешь убивать?",
        ],
        POLICEMAN_CHECKS_CB: [
            police_check_cb_data,
            "Кого будешь проверять?",
        ],
    }
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=callback.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    police_action = data[callback.data]
    markup = send_selection_to_players_kb(
        players_ids=game_data["players_ids"],
        players=game_data["players"],
        extra_buttons=(POLICEMAN_BACK_BTN,),
        exclude=callback.from_user.id,
        user_index_cb=police_action[0],
    )
    await callback.message.edit_text(
        text=police_action[1], reply_markup=markup
    )


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS, F.data == PLAYER_BACKS_CB
)
async def policeman_cancels_selection(callback: CallbackQuery):
    await callback.message.edit_text(
        text=Policeman.mail_message,
        reply_markup=kill_or_check_on_policeman(),
    )


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS,
    PoliceActionIndexCbData.filter(
        F.check_or_kill == CheckOrKill.kill
    ),
)
async def policeman_chose_to_kill(
    callback: CallbackQuery,
    callback_data: PoliceActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    await take_action_and_register_user(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
    )


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS,
    PoliceActionIndexCbData.filter(
        F.check_or_kill == CheckOrKill.check
    ),
)
async def policeman_chose_to_check(
    callback: CallbackQuery,
    callback_data: PoliceActionIndexCbData,
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
    checked_user_id = game_data["players_ids"][
        callback_data.user_index
    ]
    role = game_data["players"][str(checked_user_id)]["pretty_role"]
    url = game_data["players"][str(checked_user_id)]["url"]
    game_data["disclosed_roles"].append([checked_user_id, role])
    await callback.message.delete()
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text="Армия насильно заставила кого-то показать документы",
    )
    await asyncio.gather(
        *(
            callback.bot.send_message(
                chat_id=policeman_id,
                text=f"{game_data['players'][str(callback.from_user.id)]['pretty_role']} "
                f"{game_data['players'][str(callback.from_user.id)]['url']} "
                f"решил проверить {url}",
            )
            for policeman_id in game_data[
                Roles.policeman.value.roles_key
            ]
        )
    )
