from aiogram import F, Router
from aiogram.enums import ChatType
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)

from .ban_roles import router as ban_roles_router
from .help import router as help_router
from .order_of_roles import router as order_of_roles_router
from .profiles import router as profile_router
from .settings import router as settings_router
from .start import router as start_router
from .time import router as time_router
from .different_settings import router as fog_of_war_router

router = Router(name=__name__)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
router.message.middleware(DatabaseMiddlewareWithCommit())
router.message.middleware(DatabaseMiddlewareWithoutCommit())
router.callback_query.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithoutCommit())


always_available_router = Router(name=__name__)
always_available_router.message.filter(
    F.chat.type == ChatType.PRIVATE
)
always_available_router.message.middleware(
    DatabaseMiddlewareWithoutCommit()
)
always_available_router.include_routers(
    profile_router,
    help_router,
)


router.include_routers(
    ban_roles_router,
    order_of_roles_router,
    start_router,
    settings_router,
    time_router,
    fog_of_war_router,
)
