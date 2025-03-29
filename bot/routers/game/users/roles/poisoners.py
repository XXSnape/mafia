from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from constants.output import NUMBER_OF_NIGHT
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import (
    POLICEMAN_KILLS_CB,
    POISONER_POISONS_CB,
    PLAYER_BACKS_CB,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
    kill_or_poison_kb,
)
from keyboards.inline.buttons.common import BACK_BTN
from services.game.actions_at_night import (
    get_game_state_and_data,
    take_action_and_save_data,
)
from services.game.roles.poisoner import Poisoner
from services.game.saving_role_selection.poisoner import PoisonerSaver
from states.states import UserFsm
from utils.tg import delete_message

router = Router(name=__name__)


@router.callback_query(
    UserFsm.POISONER_CHOOSES_ACTION, F.data == POLICEMAN_KILLS_CB
)
async def poisoner_chose_to_kill(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PoisonerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.poisoner_chose_to_kill()
    # game_state, game_data = await get_game_state_and_data(
    #     tg_obj=callback,
    #     state=state,
    #     dispatcher=dispatcher,
    # )
    # poisoned = game_data[Poisoner.extra_data[0].key]
    # poisoned[1] = 1
    # await delete_message(callback.message)
    # await callback.message.answer(
    #     text=NUMBER_OF_NIGHT.format(game_data["number_of_night"])
    #     + "Ты решил всех убить!"
    # )
    # await game_state.set_data(game_data)


@router.callback_query(
    UserFsm.POISONER_CHOOSES_ACTION, F.data == POISONER_POISONS_CB
)
async def poisoner_poisons(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PoisonerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.poisoner_poisons()
    # game_state, game_data = await get_game_state_and_data(
    #     tg_obj=callback,
    #     state=state,
    #     dispatcher=dispatcher,
    # )
    # poisoned = game_data[Poisoner.extra_data[0].key]
    # exclude = (poisoned[0] if poisoned else []) + [
    #     callback.from_user.id
    # ]
    # await state.set_state(UserFsm.POISONER_CHOSE_TO_KILL)
    # await callback.message.edit_text(
    #     "Кого собираешься отравить?",
    #     reply_markup=send_selection_to_players_kb(
    #         players_ids=game_data["players_ids"],
    #         players=game_data["players"],
    #         extra_buttons=(BACK_BTN,),
    #         exclude=exclude,
    #     ),
    # )


@router.callback_query(
    UserFsm.POISONER_CHOSE_TO_KILL, F.data == PLAYER_BACKS_CB
)
async def poisoner_cancels_selection(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PoisonerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.poisoner_cancels_selection()
    # _, game_data = await get_game_state_and_data(
    #     tg_obj=callback,
    #     state=state,
    #     dispatcher=dispatcher,
    # )
    # poisoned = game_data[Poisoner.extra_data[0].key]
    # await state.set_state(UserFsm.POISONER_CHOOSES_ACTION)
    # await callback.message.edit_text(
    #     text=Poisoner.mail_message,
    #     reply_markup=kill_or_poison_kb(poisoned=poisoned),
    # )


@router.callback_query(
    UserFsm.POISONER_CHOSE_TO_KILL,
    UserActionIndexCbData.filter(),
)
async def poisoner_chose_victim(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PoisonerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.poisoner_chose_victim(callback_data=callback_data)
    # game_state, game_data, user_id = (
    #     await take_action_and_register_user(
    #         callback=callback,
    #         callback_data=callback_data,
    #         state=state,
    #         dispatcher=dispatcher,
    #     )
    # )
    # poisoned = game_data[Poisoner.extra_data[0].key]
    # if poisoned:
    #     poisoned[0].append(user_id)
    # else:
    #     poisoned[:] = [[user_id], 0]
    # await game_state.set_data(game_data)
