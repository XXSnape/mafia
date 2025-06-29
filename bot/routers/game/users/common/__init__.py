from aiogram import Router

from .after_death import router as after_death_router
from .allies_communicate import router as allies_communicate_router
from .join_to_game import router as join_to_game_router
from .refuse_move import router as refuse_move_router
from .voting import router as voting_roter

router = Router(name=__name__)
router.include_routers(
    after_death_router,
    voting_roter,
    allies_communicate_router,
    join_to_game_router,
    refuse_move_router,
)
