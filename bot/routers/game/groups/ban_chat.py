from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from cache.cache_types import GameCache
from services.game.processing_actions_in_group import GroupManager
from services.game.roles import Prosecutor
from states.states import GameFsm

router = Router(name=__name__)


@router.message(StateFilter(GameFsm.STARTED, GameFsm.VOTE))
async def delete_message_from_non_players(
    message: Message, state: FSMContext
):
    group_manager = GroupManager(message=message, state=state)
    await group_manager.delete_message_from_non_players()
    # game_data: GameCache = await state.get_data()
    # if (
    #     message.from_user.id not in game_data["players_ids"]
    # ) or message.from_user.id == Prosecutor().get_processed_user_id(
    #     game_data
    # ):
    #     await message.delete()
    # await message.chat.restrict(
    #     user_id=message.from_user.id,
    #     permissions=ChatPermissions(can_send_messages=False),
    #     until_date=timedelta(seconds=30),
    # )
