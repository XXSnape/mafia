from mypy.build import TypedDict


# class CacheData(TypedDict, total=False):
#     players_ids: list[int]
#     owner: int
#     mafias: list[int]
#     doctors: list[int]
#     policeman: list[int]
#     died: list[int]


class Player(TypedDict, total=False):
    is_alive: bool
    can_vote: bool


ROLES = ("mafia", "doctor", "policeman", "civilian")
