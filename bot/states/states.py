from aiogram.fsm.state import State, StatesGroup


class GameFsm(StatesGroup):
    REGISTRATION = State()
    STARTED = State()


class UserFsm(StatesGroup):
    REGISTRATION = State()
    MAFIA_ATTACKS = State()
    DOCTOR_TREATS = State()
    POLICEMAN_CHECKS = State()
