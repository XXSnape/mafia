from cache.cache_types import RolesLiteral
from database.schemas.settings import DifferentSettingsSchema
from pydantic import BaseModel


class GroupSettingsSchema(DifferentSettingsSchema):
    id: int
    banned_roles: list[RolesLiteral]
    order_of_roles: list[RolesLiteral]
    is_there_settings: bool


class GroupIdSchema(BaseModel):
    group_id: int


class GroupSettingIdSchema(BaseModel):
    setting_id: int | None
