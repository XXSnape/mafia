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
    sleeper = roles.Sleeper()
    policeman = roles.Policeman()
    doctor = roles.Doctor()
    # sleeper = roles.Sleeper()
    # punisher = roles.Punisher()
    # killer = roles.Killer()

    # sleeper = roles.Sleeper()
    # agent = roles.Agent()
    # lucky_gay = roles.LuckyGay()
    # bodyguard = roles.Bodyguard()
    # policeman = roles.Policeman()
    # angel_of_death = roles.AngelOfDeath()
    # general = roles.PolicemanAlias()
    # journalist = roles.Journalist()

    # sleeper = roles.Sleeper()
    # werewolf = roles.Werewolf()
    # policeman = roles.Policeman()
    # doctor = roles.Doctor()
    # angel_of_death = roles.AngelOfDeath()
    # mafia = roles.MafiaAlias()
    # killer = roles.Killer()
    # punisher = roles.Punisher()
    # policeman = roles.Policeman()

    # werewolf = roles.Werewolf()
    # sleeper = roles.Sleeper()
    # angel_of_death = roles.AngelOfDeath()

    # werewolf = roles.Werewolf()
    # punisher = roles.Punisher()
    # hacker = roles.Hacker()
    # forger = roles.Forger()
    # agent = roles.Agent()
    # journalist = roles.Journalist()
    # prosecutor = roles.Prosecutor()
    # analyst = roles.Analyst()
    # civilian = roles.Civilian()
    # lawyer = roles.Lawyer()
    # lucky_gay = roles.LuckyGay()
    # traitor = roles.Traitor()
    # suicide_bomber = roles.SuicideBomber()
    # masochist = roles.Masochist()
    # killer = roles.Killer()
    # bodyguard = roles.Bodyguard()
    # policeman = roles.Policeman()
    # general = roles.PolicemanAlias()
    # mafia = roles.MafiaAlias()
    # nurse = roles.DoctorAlias()
    # instigator = roles.Instigator()
    # prime_minister = roles.PrimeMinister()
    # doctor = roles.Doctor()
