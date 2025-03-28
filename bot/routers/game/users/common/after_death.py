from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from cache.cache_types import GameCache, UserCache
from states.states import UserFsm
from utils.utils import get_state_and_assign, make_build

router = Router(name=__name__)


@router.message(F.text, UserFsm.WAIT_FOR_LATEST_LETTER)
async def send_latest_message(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=message.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    role = game_data["players"][str(message.from_user.id)]["role"]
    url = game_data["players"][str(message.from_user.id)]["url"]
    await message.bot.send_message(
        chat_id=user_data["game_chat"],
        text=f"По слухам {role} {url} перед смертью проглаголил такие слова:\n\n{message.text}",
    )
    await message.answer(make_build("Сообщение успешно отправлено!"))
    await state.set_state(state=None)
