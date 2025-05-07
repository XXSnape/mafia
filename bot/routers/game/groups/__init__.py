from aiogram import F, Router
from aiogram.enums import ChatType

from .confirm_vote import router as confirm_vote_router
from .messages_during_game import router as ban_chat_router
from .registration import router as registration_router

router = Router(name=__name__)

router.message.filter(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
router.callback_query.filter(
    F.message.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)

router.include_routers(
    ban_chat_router, registration_router, confirm_vote_router
)
