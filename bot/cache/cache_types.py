from typing import TypedDict


class UserGameCache(TypedDict):
    fullname: str


class GameCache(TypedDict):
    owner: int
    players_ids: list[int]
    players: dict[str, UserGameCache]
