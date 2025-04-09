from typing import overload, Final

from cache.cache_types import RolesLiteral
from mafia import roles
from mafia.roles import RoleABC, ActiveRoleAtNightABC


@overload
def get_data_with_roles() -> dict[RolesLiteral, RoleABC]: ...


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


BASES_ROLES: Final[tuple[RolesLiteral, ...]] = (
    roles.Mafia.role_id,
    roles.Policeman.role_id,
    roles.Doctor.role_id,
    roles.Warden.role_id,
)

REQUIRED_ROLES: Final[tuple[RolesLiteral, ...]] = BASES_ROLES + (
    roles.MafiaAlias.role_id,
)
