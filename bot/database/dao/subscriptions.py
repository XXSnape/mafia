from database.dao.base import BaseDAO
from database.models import SubscriptionModel


class SubscriptionsDAO(BaseDAO[SubscriptionModel]):
    model = SubscriptionModel
