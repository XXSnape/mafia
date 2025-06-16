from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from general.commands import GroupCommands
from services.game.processing_actions_in_group import GroupManager
from states.game import GameFsm

router = Router(name=__name__)


@router.message(
    StateFilter(GameFsm.STARTED), Command(GroupCommands.leave.name)
)
async def want_to_exit_game(message: Message, state: FSMContext):
    group_manager = GroupManager(message=message, state=state)
    await group_manager.want_to_exit_game()


@router.message(StateFilter(GameFsm.STARTED))
async def delete_message_from_non_players(
    message: Message, state: FSMContext
):
    group_manager = GroupManager(message=message, state=state)
    await group_manager.delete_message_from_non_players()
