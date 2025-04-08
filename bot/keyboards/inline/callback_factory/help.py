from aiogram.filters.callback_data import CallbackData

from cache.cache_types import RolesLiteral


class RoleCbData(CallbackData, prefix="role"):
    role_id: RolesLiteral
