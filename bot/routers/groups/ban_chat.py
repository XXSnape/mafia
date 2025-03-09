from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from cache.cache_types import GameCache
from services.roles import Prosecutor
from states.states import GameFsm

router = Router(name=__name__)


@router.message(GameFsm.STARTED)
async def delete_message_from_non_players(
    message: Message, state: FSMContext
):
    game_data: GameCache = await state.get_data()
    if (
        message.from_user.id not in game_data["players_ids"]
    ) or message.from_user.id == Prosecutor().get_processed_user_id(
        game_data
    ):
        await message.delete()
        # await message.chat.restrict(
        #     user_id=message.from_user.id,
        #     permissions=ChatPermissions(can_send_messages=False),
        #     until_date=timedelta(seconds=30),
        # )
