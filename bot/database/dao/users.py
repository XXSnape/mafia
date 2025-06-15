from loguru import logger
from sqlalchemy.exc import IntegrityError

from database.dao.base import BaseDAO
from database.dao.settings import SettingsDao
from database.models import UserModel
from database.schemas.bids import UserMoneySchema
from database.schemas.common import TgIdSchema, UserTgIdSchema
from sqlalchemy import update

from general.exceptions import NotEnoughMoney
from general.resources import Resources
from general.text import MONEY_SYM


class UsersDao(BaseDAO[UserModel]):
    model = UserModel

    async def update_balance(
        self,
        user_money: UserMoneySchema,
        add_money: bool,
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

    async def update_assets(
        self,
        tg_id: TgIdSchema,
        asset: Resources,
        cost: int,
        count: int,
    ):
        user = await self.get_user_or_create(tg_id)
        if user.balance - cost < 0:
            raise NotEnoughMoney(balance=user.balance)
        asset_name = asset.value
        user.balance -= cost
        setattr(user, asset_name, getattr(user, asset_name) + count)
        try:
            await self._session.flush()
            logger.info(
                "Пользователь {} приобрел {} в количестве {} штук за {}{}",
                user.tg_id,
                asset_name,
                count,
                cost,
                MONEY_SYM,
            )
        except IntegrityError as e:
            await self._session.rollback()
            logger.exception(
                "Ошибка у пользователя {} во время покупки {}",
                TgIdSchema.tg_id,
                asset,
            )
            raise e

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
