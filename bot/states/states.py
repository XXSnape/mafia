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
    INSTIGATOR_CHOOSES_SUBJECT = State()
    INSTIGATOR_CHOOSES_OBJECT = State()
    INSTIGATOR_LYING = State()
    ANGEL_TAKES_REVENGE = State()
    ANALYST_ASSUMES = State()
    JOURNALIST_TAKES_INTERVIEW = State()
    AGENT_WATCHES = State()
    CLOFFELINE_GIRL_PUTS_TO_SLEEP = State()
    KILLER_ATTACKS = State()
    DON_ATTACKS = State()
    FORGER_FAKES = State()
    WEREWOLF_TURNS_INTO = State()
    TRAITOR_FINDS_OUT = State()
    WAIT_FOR_LATEST_LETTER = State()
