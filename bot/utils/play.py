from aiogram.fsm.context import FSMContext
from mypy.build import TypedDict
from random import shuffle

from cache.keys import PLAYERS_IDS_KEY


class CacheData(TypedDict, total=False):
    players_ids: list[int]
    owner: int
    mafias: list[int]
    doctors: list[int]
    policeman: list[int]
    died: list[int]


class Player(TypedDict, total=False):
    is_alive: bool
    can_vote: bool


PLAYERS = ("mafia", "doctor", "policeman")


async def select_roles(state: FSMContext):
    ids = (await state.get_data())[PLAYERS_IDS_KEY]
    if len(ids) < 3:
        return
    for user_id in ids:
        await state.update_data(
            {str(user_id): {"is_alive": True, "can_vote": True}}
        )
    shuffle(ids)
    mafias = [ids[0]]
    doctors = [ids[1]]
    policeman = [ids[2]]
    died = []
    await state.update_data(
        {
            "mafias": mafias,
            "doctors": doctors,
            "policeman": policeman,
            "died": died,
        }
    )
