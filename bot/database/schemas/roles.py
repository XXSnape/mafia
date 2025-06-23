from cache.cache_types import RolesLiteral
from database.schemas.common import UserTgIdSchema
from database.schemas.groups import GroupIdSchema


class ProhibitedRoleSchema(GroupIdSchema):
    role_id: RolesLiteral


class OrderOfRolesSchema(GroupIdSchema):
    role_id: RolesLiteral
    number: int
