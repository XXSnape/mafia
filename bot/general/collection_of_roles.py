from typing import overload

from cache.cache_types import RolesLiteral
from mafia import roles
from mafia.roles import RoleABC, ActiveRoleAtNightABC


@overload
def get_data_with_roles() -> dict[str, RoleABC]: ...


@overload
def get_data_with_roles(
    role_id: RolesLiteral,
) -> RoleABC | ActiveRoleAtNightABC: ...


def get_data_with_roles(
    role_id: RolesLiteral | None = None,
):
    roles_data = [
        roles.Mafia(),
        roles.Doctor(),
        roles.Policeman(),
        roles.Civilian(),
        roles.MafiaAlias(),
        roles.Traitor(),
        roles.Killer(),
        roles.Werewolf(),
        roles.Forger(),
        roles.Hacker(),
        roles.Sleeper(),
        roles.Agent(),
        roles.Journalist(),
        roles.Punisher(),
        roles.Analyst(),
        roles.SuicideBomber(),
        roles.Instigator(),
        roles.PrimeMinister(),
        roles.Poisoner(),
        roles.Bodyguard(),
        roles.Masochist(),
        roles.Lawyer(),
        roles.AngelOfDeath(),
        roles.Prosecutor(),
        roles.LuckyGay(),
        roles.DoctorAliasABC(),
        roles.PolicemanAliasABC(),
        roles.Warden(),
    ]
    all_roles = {role.role_id: role for role in roles_data}
    if role_id:
        return all_roles[role_id]
    return all_roles


BASES_ROLES = [
    # roles.Journalist.role_id,
    roles.Mafia.role_id,
    roles.MafiaAlias.role_id,
    roles.MafiaAlias.role_id,
    roles.Sleeper.role_id,
    # roles.Doctor.role_id,
    # roles.Bodyguard.role_id,
    # roles.Killer.role_id,
    # roles.Poisoner.role_id,
    # roles.AngelOfDeath.role_id,
    # roles.Traitor.role_id,
    # roles.Werewolf.role_id,
    # roles.Journalist.role_id,
    # roles.Poisoner.role_id,
]
REQUIRED_ROLES = BASES_ROLES + ["mafia"]

# TESTED 2
# bodyguard
# nurse
# doctor
# policeman
# general
# don
# mafia
# killer
# traitor
# werewolf
# civilian
# angel_of_death
# hacker
# analyst
# prime_minister
# lawyer
# instigator
# suicide_bomber
# masochist
# lucky_gay
# prosecutor
# forger
# agent
# journalist
