from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from services.game.processing_user_actions import UserManager
from states.states import UserFsm

router = Router(name=__name__)


@router.message(F.text, UserFsm.WAIT_FOR_LATEST_LETTER)
async def send_latest_message(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_manager = UserManager(
        message=message, state=state, dispatcher=dispatcher
    )
    await user_manager.send_latest_message()
    # user_data: UserCache = await state.get_data()
    # game_state = await get_state_and_assign(
    #     dispatcher=dispatcher,
    #     chat_id=user_data["game_chat"],
    #     bot_id=message.bot.id,
    # )
    # game_data: GameCache = await game_state.get_data()
    # role = game_data["players"][str(message.from_user.id)][
    #     "pretty_role"
    # ]
    # url = game_data["players"][str(message.from_user.id)]["url"]
    # await message.bot.send_message(
    #     chat_id=user_data["game_chat"],
    #     text=f"По слухам {role} {url} перед смертью проглаголил такие слова:\n\n{message.text}",
    # )
    # await message.answer(make_build("Сообщение успешно отправлено!"))
    # await state.set_state(state=None)
