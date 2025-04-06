from pydantic import BaseModel

from cache.cache_types import RolesLiteral


class GroupSettingsSchema(BaseModel):
    id: int
    banned_roles: list[RolesLiteral] | None = None
    order_of_roles: list[RolesLiteral] | None = None
    time_for_night: int | None = None
    time_for_day: int | None = None


class GroupSettingIdSchema(BaseModel):
    setting_id: int | None
