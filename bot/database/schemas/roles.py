from cache.cache_types import RolesLiteral
from database.schemas.common import UserTgIdSchema


class ProhibitedRoleSchema(UserTgIdSchema):
    role_id: RolesLiteral


class OrderOfRolesSchema(UserTgIdSchema):
    role_id: RolesLiteral
    number: int
