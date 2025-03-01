from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData


class ProsAndCons(IntEnum):
    pros = auto()
    cons = auto()


class UserActionIndexCbData(CallbackData, prefix="user"):
    user_index: int


class UserVoteIndexCbData(UserActionIndexCbData, prefix="vote"):
    pass


class AimedUserCbData(CallbackData, prefix="aim"):
    user_id: int
    action: ProsAndCons
