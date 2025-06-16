from aiogram import F, Router
from aiogram.enums import ChatType

from .common import router as common_router
from .common.anonymizer import router as anonymizer_router
from .roles import router as roles_router

router = Router(name=__name__)

always_available_router = Router(name=__name__)
always_available_router.include_router(anonymizer_router)


router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
router.include_routers(common_router, roles_router)
