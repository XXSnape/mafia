from database.dao.base import BaseDAO
from database.models import ResultModel


class ResultsDao(BaseDAO[ResultModel]):
    model = ResultModel
