from cache.cache_types import RolesLiteral
from general.collection_of_roles import get_data_with_roles


def sort_roles_by_name(role_key: RolesLiteral):
    return get_data_with_roles(role_key).role
