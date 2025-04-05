from cache.cache_types import RolesLiteral
from database.schemas.common import UserTgId


class ProhibitedRoleSchema(UserTgId):
    role_id: RolesLiteral


class OrderOfRolesSchema(UserTgId):
    role_id: RolesLiteral
    number: int
