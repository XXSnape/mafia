from aiogram.fsm.state import State
from telebot.states import StatesGroup


class SettingsFsm(StatesGroup):
    BAN_ROLES = State()
