import enum
from typing import overload

from cache.cache_types import RolesLiteral
from services import roles
from services.roles.base import Role, ActiveRoleAtNight


@overload
def get_data_with_roles(role_name: None) -> dict[str, Role]: ...


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
    if role_name:
        return all_roles[role_name]
    return all_roles


class Roles(enum.Enum):
    don = roles.Mafia()
    # journalist = roles.Journalist()
    doctor = roles.Doctor()
    masochist = roles.Masochist()
    policeman = roles.Policeman()

    # doctor = roles.Doctor()
    # civilian = roles.Civilian()
    # instigator = roles.Instigator()
    # general = roles.PolicemanAlias()
    # sleeper = roles.Sleeper()
    # punisher = roles.Punisher()
    # killer = roles.Killer()
    # agent = roles.Agent()
    # lucky_gay = roles.LuckyGay()
    # bodyguard = roles.Bodyguard()
    # angel_of_death = roles.AngelOfDeath()
    # journalist = roles.Journalist()
    # werewolf = roles.Werewolf()
    # mafia = roles.MafiaAlias()
    # hacker = roles.Hacker()
    # forger = roles.Forger()
    # prosecutor = roles.Prosecutor()
    # analyst = roles.Analyst()
    # lawyer = roles.Lawyer()
    # traitor = roles.Traitor()
    # suicide_bomber = roles.SuicideBomber()
    # masochist = roles.Masochist()
    # nurse = roles.DoctorAlias()
    # prime_minister = roles.PrimeMinister()

    # civilian = roles.Civilian()
    # nurse = roles.DoctorAlias()
