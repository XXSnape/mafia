from aiogram import Router
from .bodyguards import router as bodyguards_router
from .doctors import router as doctors_router
from .mafias import router as mafias_router
from .policeman import router as policeman_router
from .prosecutors import router as prosecutors_router
from .lawyers import router as lawyers_router

router = Router(name=__name__)
router.include_routers(
    bodyguards_router,
    doctors_router,
    mafias_router,
    policeman_router,
    prosecutors_router,
    lawyers_router,
)
