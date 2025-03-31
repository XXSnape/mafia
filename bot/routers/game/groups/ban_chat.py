from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from services.game.processing_actions_in_group import GroupManager
from states.states import GameFsm

router = Router(name=__name__)


@router.message(StateFilter(GameFsm.STARTED))
async def delete_message_from_non_players(
    message: Message, state: FSMContext
):
    group_manager = GroupManager(message=message, state=state)
    await group_manager.delete_message_from_non_players()
