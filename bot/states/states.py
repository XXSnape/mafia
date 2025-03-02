from aiogram.fsm.state import State, StatesGroup


class GameFsm(StatesGroup):
    REGISTRATION = State()
    STARTED = State()
    VOTE = State()


class UserFsm(StatesGroup):
    REGISTRATION = State()
    MAFIA_ATTACKS = State()
    DOCTOR_TREATS = State()
    POLICEMAN_CHECKS = State()
    PROSECUTOR_ARRESTS = State()
    LAWYER_PROTECTS = State()
    BODYGUARD_PROTECTS = State()
    WAIT_FOR_LATEST_LETTER = State()
