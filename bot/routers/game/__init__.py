from aiogram import Router

from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)
from middlewares.time_limits import CallbackTimelimiterMiddleware
from .users import router as users_router
from .groups import router as groups_router


router = Router(name=__name__)


router.message.middleware(DatabaseMiddlewareWithCommit())
router.message.middleware(DatabaseMiddlewareWithoutCommit())
router.callback_query.middleware(CallbackTimelimiterMiddleware())
router.callback_query.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithoutCommit())

router.include_routers(
    groups_router,
    users_router,
)
