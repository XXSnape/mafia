from database.dao.base import BaseDAO
from database.models import AssetModel


class AssetsDao(BaseDAO[AssetModel]):
    model = AssetModel
