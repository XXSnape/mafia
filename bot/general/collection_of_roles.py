from typing import Final, TypeAlias, overload

from cache.cache_types import RolesLiteral
from mafia import roles
from mafia.roles import ActiveRoleAtNightABC, RoleABC

DataWithRoles: TypeAlias = dict[RolesLiteral, RoleABC]


@overload
def get_data_with_roles() -> DataWithRoles: ...


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
        roles.Lucifer(),
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
        roles.DoctorAlias(),
        roles.PolicemanAlias(),
        roles.Warden(),
    ]
    all_roles = {role.role_id: role for role in roles_data}
    if role_id:
        return all_roles[role_id]
    return all_roles


BASES_ROLES: Final[tuple[RolesLiteral, ...]] = (
    roles.Civilian.role_id,
    roles.Doctor.role_id,
    roles.Mafia.role_id,
    roles.Policeman.role_id,
)

REQUIRED_ROLES: Final[tuple[RolesLiteral, ...]] = BASES_ROLES + (
    roles.MafiaAlias.role_id,
)
