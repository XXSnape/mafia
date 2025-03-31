from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.cb.cb_text import (
    WEREWOLF_TO_DOCTOR_CB,
    WEREWOLF_TO_MAFIA_CB,
    WEREWOLF_TO_POLICEMAN_CB,
)
from services.game.saving_role_selection.werewolf import (
    WerewolfSaver,
)
from states.states import UserFsm


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
    saver = WerewolfSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.werewolf_turns_into()
