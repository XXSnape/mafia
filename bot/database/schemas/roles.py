from pydantic import BaseModel

from cache.cache_types import RolesLiteral


class UserId(BaseModel):
    tg_id: int


class UserTgId(BaseModel):
    user_tg_id: int


class ProhibitedRoleSchema(UserTgId):
    role_id: RolesLiteral


class OrderOfRolesSchema(UserTgId):
    role_id: RolesLiteral
    number: int
