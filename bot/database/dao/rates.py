from database.dao.base import BaseDAO
from database.models import RateModel


class RatesDao(BaseDAO[RateModel]):
    model = RateModel
