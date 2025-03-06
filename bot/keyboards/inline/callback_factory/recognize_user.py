from enum import IntEnum, auto
from functools import partial

from aiogram.filters.callback_data import CallbackData


class ProsAndCons(IntEnum):
    pros = auto()
    cons = auto()


class CheckOrKill(IntEnum):
    check = auto()
    kill = auto()


class UserActionIndexCbData(CallbackData, prefix="user"):
    user_index: int


class UserVoteIndexCbData(UserActionIndexCbData, prefix="vote"):
    pass


class PoliceActionIndexCbData(
    UserActionIndexCbData, prefix="police"
):
    check_or_kill: CheckOrKill


police_kill_cb_data = partial(
    PoliceActionIndexCbData, check_or_kill=CheckOrKill.kill
)
police_check_cb_data = partial(
    PoliceActionIndexCbData, check_or_kill=CheckOrKill.check
)


class AimedUserCbData(CallbackData, prefix="aim"):
    user_id: int
    action: ProsAndCons
