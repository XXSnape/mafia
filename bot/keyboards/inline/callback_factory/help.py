from aiogram.filters.callback_data import CallbackData
from cache.cache_types import RolesLiteral


class RoleCbData(CallbackData, prefix="role"):
    role_id: RolesLiteral


class OrderOfRolesCbData(RoleCbData, prefix="order_of_roles"):
    pass


class BannedRolesCbData(RoleCbData, prefix="banned_roles"):
    pass
