from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from cache.cache_types import GameCache
from states.states import GameFsm

router = Router(name=__name__)


@router.message(GameFsm.STARTED)
async def delete_message_from_non_players(
    message: Message, state: FSMContext
):
    game_data: GameCache = await state.get_data()
    if (
        message.from_user.id not in game_data["players_ids"]
    ) or message.from_user.id in game_data["cant_vote"]:
        await message.delete()
        # await message.chat.restrict(
        #     user_id=message.from_user.id,
        #     permissions=ChatPermissions(can_send_messages=False),
        #     until_date=timedelta(seconds=30),
        # )
