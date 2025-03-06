from aiogram import Router

from .bodyguards import router as bodyguards_router
from .doctors import router as doctors_router
from .mafias import router as mafias_router
from .policeman import router as policeman_router
from .prosecutors import router as prosecutors_router
from .lawyers import router as lawyers_router
from .instigators import router as instigators_router
from .angels_of_death import router as angels_of_death_router
from .analysts import router as analysts_router
from .journalists import router as journalists_router
from .agents import router as agents_router
from .sleepers import router as sleepers_router
from .killers import router as killers_router
from .forgers import router as forgers_router

router = Router(name=__name__)
router.include_routers(
    bodyguards_router,
    doctors_router,
    mafias_router,
    policeman_router,
    prosecutors_router,
    lawyers_router,
    instigators_router,
    angels_of_death_router,
    analysts_router,
    journalists_router,
    agents_router,
    sleepers_router,
    killers_router,
    forgers_router,
)
