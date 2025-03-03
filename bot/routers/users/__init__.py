from aiogram import Router, F
from aiogram.enums import ChatType
from .common import router as common_router
from .roles import router as roles_router

router = Router(name=__name__)

router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
router.include_routers(common_router, roles_router)
