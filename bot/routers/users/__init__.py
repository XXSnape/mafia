from aiogram import Router, F
from aiogram.enums import ChatType

from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)
from .ban_roles import router as ban_roles_router
from .common import router as common_router
from .order_of_roles import router as order_of_roles_router
from .settings import router as settings_router
from .start import router as start_router

router = Router(name=__name__)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
router.message.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithoutCommit())

router.include_routers(
    ban_roles_router,
    order_of_roles_router,
    common_router,
    settings_router,
    start_router,
)
