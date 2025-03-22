from database.dao.base import BaseDAO
from database.models import UserModel


class UsersDao(BaseDAO[UserModel]):
    model = UserModel
