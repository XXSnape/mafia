from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    AimedUserCbData,
)
from services.game.processing_actions_in_group import GroupManager

router = Router(name=__name__)


@router.callback_query(AimedUserCbData.filter())
async def confirm_vote(
    callback: CallbackQuery,
    callback_data: AimedUserCbData,
    state: FSMContext,
):
    group_manager = GroupManager(callback=callback, state=state)
    await group_manager.confirm_vote(callback_data=callback_data)
