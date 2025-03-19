from aiogram.fsm.state import State, StatesGroup


class SettingsFsm(StatesGroup):
    BAN_ROLES = State()
