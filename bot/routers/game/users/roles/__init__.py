from aiogram import Router

from .analysts import router as analysts_router
from .base_roles import router as base_roles_router
from .forgers import router as forgers_router
from .instigators import router as instigators_router
from .poisoners import router as poisoners_router
from .policeman import router as policeman_router
from .wardens import router as wardens_router
from .werewolves import router as werewolves_router

router = Router(name=__name__)
router.include_routers(
    base_roles_router,
    poisoners_router,
    policeman_router,
    wardens_router,
    analysts_router,
    forgers_router,
    werewolves_router,
    instigators_router,
)
