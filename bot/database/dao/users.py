from sqlalchemy import update

from database.dao.base import BaseDAO
from database.dao.settings import SettingsDao
from database.models import UserModel
from database.schemas.bids import UserMoneySchema
from database.schemas.common import TgIdSchema, UserTgIdSchema


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

    async def get_user_or_create(
        self, tg_id: TgIdSchema
    ) -> UserModel:
        user = await self.find_one_or_none(filters=tg_id)
        if user:
            return user
        user = await self.add(tg_id)
        settings_dao = SettingsDao(session=self._session)
        await settings_dao.add(UserTgIdSchema(user_tg_id=user.tg_id))
        return user
