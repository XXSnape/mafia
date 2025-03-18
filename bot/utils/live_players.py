from cache.cache_types import GameCache
from services.roles.base import Role
from services.roles.base.roles import Groupings
from utils.utils import get_profiles, make_build


def get_live_players(
    game_data: GameCache, all_roles: dict[str, Role]
):
    profiles = get_profiles(
        players_ids=game_data["players_ids"],
        players=game_data["players"],
    )
    live_roles = get_live_roles(
        game_data=game_data, all_roles=all_roles
    )
    return (
        f"{make_build('💗Живые игроки:')}\n"
        f"{profiles}\n\n"
        f"{make_build('Состав группировок:')}\n"
        f"{live_roles}\n\n"
    )


def get_live_roles(game_data: GameCache, all_roles: dict[str, Role]):
    gropings: dict[Groupings, list[tuple[str, int]]] = {
        Groupings.civilians: [],
        Groupings.criminals: [],
        Groupings.killer: [],
        Groupings.other: [],
    }
    for role in all_roles:
        current_role = all_roles[role]
        if not game_data[current_role.roles_key]:
            continue
        grouping = gropings[current_role.grouping]
        text = current_role.role
        if current_role.alias:
            count = 1
        elif current_role.is_alias:
            count = len(game_data[current_role.roles_key][1:])
        else:
            count = len(game_data[current_role.roles_key])
        if count == 0:
            continue
        if count > 1:
            count_text = f" ({count})"
            text += make_build(count_text)
        grouping.append((text, count))
    result = ""
    for grouping, roles in gropings.items():
        if not roles:
            continue
        grouping_roles = "\n● ".join(role for role, _ in roles)
        total = sum(count for _, count in roles)
        total_text = make_build(f"- {total}:")
        result += f"\n{grouping.value.name} {total_text}\n● {grouping_roles}\n"
    return result
