from aiogram.filters.callback_data import CallbackData


class UserActionIndexCbData(CallbackData, prefix="user"):
    user_index: int


class UserVoteIndexCbData(UserActionIndexCbData, prefix="vote"):
    pass
