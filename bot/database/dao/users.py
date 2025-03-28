from sqlalchemy import update

from database.dao.base import BaseDAO
from database.models import UserModel
from database.schemas.bids import UserMoneySchema


class UsersDao(BaseDAO[UserModel]):
    model = UserModel

    async def update_balance(
        self, user_money: UserMoneySchema, add_money: bool
    ):
        if add_money:
            value = {
                self.model.balance: self.model.balance
                + user_money.money
            }
        else:
            value = {
                self.model.balance: self.model.balance
                - user_money.money
            }
        update_stmt = (
            update(self.model)
            .where(
                self.model.tg_id == user_money.user_tg_id,
            )
            .values(value)
        )
        await self._session.execute(update_stmt)
        await self._session.flush()
