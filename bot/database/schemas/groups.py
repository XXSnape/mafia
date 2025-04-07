from pydantic import BaseModel

from cache.cache_types import RolesLiteral


class GroupSettingsSchema(BaseModel):
    id: int
    banned_roles: list[RolesLiteral]
    order_of_roles: list[RolesLiteral]
    time_for_night: int
    time_for_day: int
    is_there_settings: bool


class GroupIdSchema(BaseModel):
    group_id: int


class GroupSettingIdSchema(BaseModel):
    setting_id: int | None
