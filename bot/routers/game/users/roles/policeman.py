import asyncio

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from constants.output import ROLE_IS_KNOWN, NUMBER_OF_NIGHT
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
    kill_or_check_on_policeman,
    send_selection_to_players_kb,
)
from keyboards.inline.buttons.common import BACK_BTN
from services.game.actions_at_night import (
    take_action_and_register_user,
    get_game_state_and_data,
    get_game_state_data_and_user_id,
    trace_all_actions,
    save_notification_message,
)
from services.game.roles import Policeman
from services.game.saving_role_selection import PolicemanSaver
from states.states import UserFsm
from utils.tg import delete_message

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
    saver = PolicemanSaver(
        callback=callback,
        state=state,
        dispatcher=dispatcher
    )
    await saver.policeman_makes_choice()
    # data = {
    #     POLICEMAN_KILLS_CB: [
    #         police_kill_cb_data,
    #         "Кого будешь убивать?",
    #     ],
    #     POLICEMAN_CHECKS_CB: [
    #         police_check_cb_data,
    #         "Кого будешь проверять?",
    #     ],
    # }
    # _, game_data = await get_game_state_and_data(
    #     tg_obj=callback,
    #     state=state,
    #     dispatcher=dispatcher,
    # )
    # police_action = data[callback.data]
    # markup = send_selection_to_players_kb(
    #     players_ids=game_data["players_ids"],
    #     players=game_data["players"],
    #     extra_buttons=(BACK_BTN,),
    #     exclude=callback.from_user.id,
    #     user_index_cb=police_action[0],
    # )
    # await callback.message.edit_text(
    #     text=police_action[1], reply_markup=markup
    # )


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS, F.data == PLAYER_BACKS_CB
)
async def policeman_cancels_selection(callback: CallbackQuery):
    saver = PolicemanSaver(
        callback=callback,
    )
    await saver.policeman_cancels_selection()
    # await callback.message.edit_text(
    #     text=Policeman.mail_message,
    #     reply_markup=kill_or_check_on_policeman(),
    # )


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
    saver = PolicemanSaver(
        callback=callback,
        state=state,
        dispatcher=dispatcher
    )
    await saver.policeman_chose_to_kill(callback_data=callback_data)
    # await take_action_and_register_user(
    #     callback=callback,
    #     callback_data=callback_data,
    #     state=state,
    #     dispatcher=dispatcher,
    # )


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
    saver = PolicemanSaver(
        callback=callback,
        state=state,
        dispatcher=dispatcher
    )
    await saver.policeman_chose_to_check(callback_data=callback_data)
    # _, game_data, checked_user_id = (
    #     await get_game_state_data_and_user_id(
    #         callback=callback,
    #         callback_data=callback_data,
    #         state=state,
    #         dispatcher=dispatcher,
    #     )
    # )
    # role_key = game_data["players"][str(checked_user_id)][
    #     "enum_name"
    # ]
    # url = game_data["players"][str(checked_user_id)]["url"]
    # game_data["disclosed_roles"].append([checked_user_id, role_key])
    # await delete_message(callback.message)
    # await callback.bot.send_message(
    #     chat_id=game_data["game_chat"],
    #     text="Армия насильно заставила кого-то показать документы",
    # )
    # trace_all_actions(
    #     callback=callback,
    #     game_data=game_data,
    #     user_id=checked_user_id,
    # )
    # save_notification_message(
    #     game_data=game_data,
    #     processed_user_id=checked_user_id,
    #     message=ROLE_IS_KNOWN,
    #     current_user_id=callback.from_user.id,
    # )
    # await asyncio.gather(
    #     *(
    #         callback.bot.send_message(
    #             chat_id=policeman_id,
    #             text=NUMBER_OF_NIGHT.format(
    #                 game_data["number_of_night"]
    #             )
    #             + f"{game_data['players'][str(callback.from_user.id)]['pretty_role']} "
    #             f"{game_data['players'][str(callback.from_user.id)]['url']} "
    #             f"решил проверить {url}",
    #         )
    #         for policeman_id in game_data[Policeman.roles_key]
    #     )
    # )
