from aiogram import Router

from .after_death import router as after_death_router
from .allies_communicate import router as allies_communicate_router
from .voting import router as voting_roter

router = Router(name=__name__)
router.include_routers(
    after_death_router, voting_roter, allies_communicate_router
)
