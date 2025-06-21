from aiogram.fsm.state import State, StatesGroup


class GameFsm(StatesGroup):
    REGISTRATION = State()
    STARTED = State()
    WAIT_FOR_STARTING_GAME = State()


class UserFsm(StatesGroup):
    BASIC_NIGHT_ROLE = State()
    BASIC_ROLE_WITH_ALLIES = State()
    ANALYST = State()
    FORGER = State()
    POLICEMAN = State()
    WARDEN = State()
    WEREWOLF = State()
    INSTIGATOR_CHOOSES_SUBJECT = State()
    INSTIGATOR_CHOOSES_OBJECT = State()
    PIRATE_CHOOSES_SUBJECT = State()
    PIRATE_CHOOSES_OBJECT = State()
    POISONER_CHOOSES_ACTION = State()
    POISONER_CHOSE_TO_KILL = State()
    WAIT_FOR_LATEST_LETTER = State()
