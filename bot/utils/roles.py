from general.collection_of_roles import get_data_with_roles


def get_roles_without_bases(number: int):
    all_roles = get_data_with_roles()
    for role in ("don", "doctor", "policeman", "civilian", "mafia"):
        all_roles.pop(role)
    roles = sorted(role.role for role in all_roles.values())
    len_roles = len(roles)
    delimiter = 10
    for divider in range(10, 0, -1):
        if len_roles % divider != 1:
            delimiter = divider
            break
    max_number = len(roles) // delimiter + bool(
        len(roles) % delimiter
    )
    return (
        roles[number * delimiter : (number + 1) * delimiter],
        max_number - 1,
    )
