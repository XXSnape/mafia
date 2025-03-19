from aiogram.fsm.state import State, StatesGroup


class SettingsFsm(StatesGroup):
    BAN_ROLES = State()
    ORDER_OF_ROLES = State()
