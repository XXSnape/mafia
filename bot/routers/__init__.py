from aiogram import F, Router
from aiogram.enums import ChatType
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)

from .game.users import always_available_router as game_users_always_available_router
from .users import always_available_router as users_always_available_router

always_available_router = Router(name=__name__)
always_available_router.message.filter(
    F.chat.type == ChatType.PRIVATE
)
always_available_router.message.middleware(
    DatabaseMiddlewareWithoutCommit()
)
always_available_router.message.middleware(
    DatabaseMiddlewareWithCommit()
)
always_available_router.callback_query.middleware(
    DatabaseMiddlewareWithCommit()
)
always_available_router.callback_query.middleware(
    DatabaseMiddlewareWithoutCommit()
)
always_available_router.include_routers(
    users_always_available_router,
    game_users_always_available_router,
)
