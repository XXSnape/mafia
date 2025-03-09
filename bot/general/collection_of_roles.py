import enum

from services import roles


def get_data_with_roles():
    all_roles = {
        "don": roles.Mafia(),
        "doctor": roles.Doctor(),
        "policeman": roles.Policeman(),
        "traitor": roles.Traitor(),
        "killer": roles.Killer(),
        "werewolf": roles.Werewolf(),
        "forger": roles.Forger(),
        "hacker": roles.Hacker(),
        "sleeper": roles.Sleeper(),
        "agent": roles.Agent(),
        "journalist": roles.Journalist(),
        "punisher": roles.Punisher(),
        "analyst": roles.Analyst(),
        "suicide_bomber": roles.SuicideBomber(),
        "instigator": roles.Instigator(),
        "prime_minister": roles.PrimeMinister(),
        "bodyguard": roles.Bodyguard(),
        "masochist": roles.Masochist(),
        "lawyer": roles.Lawyer(),
        "angel_of_death": roles.AngelOfDeath(),
        "prosecutor": roles.Prosecutor(),
        "civilian": roles.Civilian(),
        "lucky_gay": roles.LuckyGay(),
        "mafia": roles.MafiaAlias(),
        "nurse": roles.DoctorAlias(),
        "general": roles.PolicemanAlias(),
    }

    return all_roles


class Roles(enum.Enum):
    don = roles.Mafia()
    doctor = roles.Doctor()
    policeman = roles.Policeman()

    nurse = roles.DoctorAlias()
    # traitor = roles.Traitor()
    # killer = roles.Killer()
    # werewolf = roles.Werewolf()
    # forger = roles.Forger()
    # hacker = roles.Hacker()
    # sleeper = roles.Sleeper()
    # agent = roles.Agent()
    # journalist = roles.Journalist()
    # punisher = roles.Punisher()
    # analyst = roles.Analyst()
    # suicide_bomber = roles.SuicideBomber()
    # instigator = roles.Instigator()
    # prime_minister = roles.PrimeMinister()
    # bodyguard = roles.Bodyguard()
    # masochist = roles.Masochist()
    # lawyer = roles.Lawyer()
    # angel_of_death = roles.AngelOfDeath()
    # prosecutor = roles.Prosecutor()
    # civilian = roles.Civilian()
    # lucky_gay = roles.LuckyGay()
    # mafia = roles.MafiaAlias()
    # general = roles.PolicemanAlias()
