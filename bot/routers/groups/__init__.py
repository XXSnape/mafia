from aiogram import F, Router
from aiogram.enums import ChatType
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)

from .adding import router as adding_router
from .settings import router as settings_router
from .statistics import router as statistics_router

router = Router(name=__name__)
router.message.filter(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
router.my_chat_member.middleware(DatabaseMiddlewareWithCommit())
router.message.middleware(DatabaseMiddlewareWithCommit())
router.message.middleware(DatabaseMiddlewareWithoutCommit())
router.include_routers(
    adding_router,
    settings_router,
    statistics_router,
)
