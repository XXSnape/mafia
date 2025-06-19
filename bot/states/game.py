from aiogram.fsm.state import State, StatesGroup


class GameFsm(StatesGroup):
    REGISTRATION = State()
    STARTED = State()
    WAIT_FOR_STARTING_GAME = State()


class UserFsm(StatesGroup):
    MAFIA_ATTACKS = State()
    DOCTOR_TREATS = State()
    POLICEMAN_CHECKS = State()
    PROSECUTOR_ARRESTS = State()
    LAWYER_PROTECTS = State()
    BODYGUARD_PROTECTS = State()
    INSTIGATOR_CHOOSES_SUBJECT = State()
    INSTIGATOR_CHOOSES_OBJECT = State()
    PIRATE_CHOOSES_SUBJECT = State()
    PIRATE_CHOOSES_OBJECT = State()

    ANGEL_TAKES_REVENGE = State()
    ANALYST_ASSUMES = State()
    JOURNALIST_TAKES_INTERVIEW = State()
    AGENT_WATCHES = State()
    CLOFFELINE_GIRL_PUTS_TO_SLEEP = State()
    SUPERVISOR_COLLECTS_INFORMATION = State()
    POISONER_CHOOSES_ACTION = State()
    POISONER_CHOSE_TO_KILL = State()
    KILLER_ATTACKS = State()
    DON_ATTACKS = State()
    FORGER_FAKES = State()
    WEREWOLF_TURNS_INTO = State()
    TRAITOR_FINDS_OUT = State()
    LUCIFER_BLOCKS = State()
    BRIDE_CHOOSES = State()
    MARTYR_LEARNS_ROLE = State()
    PHOENIX_RANDOMLY_ACTS = State()
    HEIR_CHOOSES_TARGET = State()
    WAIT_FOR_LATEST_LETTER = State()
