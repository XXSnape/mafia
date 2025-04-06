from database.dao.base import BaseDAO
from database.models import SettingModel


class SettingsDao(BaseDAO[SettingModel]):
    model = SettingModel
