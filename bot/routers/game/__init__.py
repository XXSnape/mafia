from aiogram import Router
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)
from middlewares.time_limits import CallbackTimelimiterMiddleware

from .groups import router as groups_router
from .users import router as users_router

router = Router(name=__name__)


router.message.middleware(DatabaseMiddlewareWithCommit())
router.message.middleware(DatabaseMiddlewareWithoutCommit())
# В норме кнопки во время игры удаляются, но если этого не произошло,
# должно срабатывать промежуточное ПО ниже и не давать пользователю возможность
# нажать на устаревшие кнопки.
router.callback_query.middleware(
    CallbackTimelimiterMiddleware(minutes=5)
)

router.callback_query.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithoutCommit())

router.include_routers(
    groups_router,
    users_router,
)
