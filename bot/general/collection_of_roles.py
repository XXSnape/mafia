import enum
from typing import overload

from cache.cache_types import RolesLiteral
from services import roles
from services.roles.base import Role, ActiveRoleAtNight


@overload
def get_data_with_roles() -> dict[str, Role]: ...


@overload
def get_data_with_roles(
    role_name: RolesLiteral,
) -> Role | ActiveRoleAtNight: ...


def get_data_with_roles(
    role_name: RolesLiteral | None = None,
):
    all_roles = {
        "don": roles.Mafia(),
        "doctor": roles.Doctor(),
        "policeman": roles.Policeman(),
        "civilian": roles.Civilian(),
        "mafia": roles.MafiaAlias(),
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
        "poisoner": roles.Poisoner(),
        "bodyguard": roles.Bodyguard(),
        "masochist": roles.Masochist(),
        "lawyer": roles.Lawyer(),
        "angel_of_death": roles.AngelOfDeath(),
        "prosecutor": roles.Prosecutor(),
        "lucky_gay": roles.LuckyGay(),
        "nurse": roles.DoctorAlias(),
        "general": roles.PolicemanAlias(),
    }
    if role_name:
        return all_roles[role_name]
    return all_roles


class Roles(enum.Enum):
    don = roles.Mafia()
    forger = roles.Forger()
    werewolf = roles.Werewolf()
    doctor = roles.Doctor()
    policeman = roles.Policeman()
    # nurse = roles.DoctorAlias()
    # policeman = roles.Policeman()
    # general = roles.PolicemanAlias()
    #
    # mafia = roles.MafiaAlias()
    # nurse = roles.DoctorAlias()
    # poisoner = roles.Poisoner()
    # punisher = roles.Punisher()
    #
    # werewolf = roles.Werewolf()
    # forger = roles.Forger()
    # nurse = roles.DoctorAlias()

    # forger = roles.Forger()
    # mafia = roles.MafiaAlias()
    # nurse = roles.DoctorAlias()
    # general = roles.PolicemanAlias()

    # werewolf = roles.Werewolf()
    # lucky_gay = roles.LuckyGay()
    # civilian = roles.Civilian()
    # traitor = roles.Traitor()
    # killer = roles.Killer()
    # mafia = roles.MafiaAlias() ?
    # hacker = roles.Hacker()
    # sleeper = roles.Sleeper()
    # journalist = roles.Journalist()
    # lawyer = roles.Lawyer()
    # prosecutor = roles.Prosecutor()
    # analyst = roles.Analyst()
    # instigator = roles.Instigator()
    # agent = roles.Agent()
    # prime_minister = roles.PrimeMinister()
    # bodyguard = roles.Bodyguard()
    # angel_of_death = roles.AngelOfDeath()
    # suicide_bomber = roles.SuicideBomber()
    # masochist = roles.Masochist()
