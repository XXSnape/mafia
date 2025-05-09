from typing import List

from database.common.base import BaseModel as Base
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class BaseDAO[M: Base]:
    model: type[M] | None = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError(
                "Модель должна быть указана в дочернем классе"
            )

    def _get_sorting_attrs(self, sort_fields: list[str]):
        return (getattr(self.model, field) for field in sort_fields)

    async def find_one_or_none_by_id(self, data_id: int) -> M | None:
        try:
            query = select(self.model).filter_by(id=data_id)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            logger.info(
                "Запись {} с ID {} {}.",
                self.model.__name__,
                data_id,
                "найдена" if record else "не найдена",
            )
            return record
        except SQLAlchemyError as e:
            logger.error(
                "Ошибка при поиске записи с ID {}: {}", data_id, e
            )
            raise

    async def find_one_or_none(self, filters: BaseModel) -> M | None:
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            "Поиск одной записи {} по фильтрам: {}",
            self.model.__name__,
            filter_dict,
        )
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            logger.info(
                "Запись {} по фильтрам: {}",
                "найдена" if record else "не найдена",
                filter_dict,
            )
            return record
        except SQLAlchemyError as e:
            logger.error(
                "Ошибка при поиске записи по фильтрам {}: {}",
                filter_dict,
                e,
            )
            raise

    async def find_all(
        self,
        filters: BaseModel | None = None,
        sort_fields: list[str] | None = None,
    ) -> list[M]:
        filter_dict = (
            filters.model_dump(exclude_unset=True) if filters else {}
        )
        logger.info(
            "Поиск всех записей {} по фильтрам: {}",
            self.model.__name__,
            filter_dict,
        )
        try:
            query = select(self.model).filter_by(**filter_dict)
            if sort_fields:
                query = query.order_by(
                    *self._get_sorting_attrs(sort_fields=sort_fields)
                )
            result = await self._session.execute(query)
            records = result.scalars().all()
            logger.info("Найдено {} записей.", len(records))
            return records
        except SQLAlchemyError as e:
            logger.error(
                "Ошибка при поиске всех записей по фильтрам {}: {}",
                filter_dict,
                e,
            )
            raise

    async def add(self, values: BaseModel) -> M:
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            "Добавление записи {} с параметрами: {}",
            self.model.__name__,
            values_dict,
        )
        try:
            new_instance = self.model(**values_dict)
            self._session.add(new_instance)
            await self._session.flush()
            logger.info(
                "Запись {} успешно добавлена.", self.model.__name__
            )
            return new_instance
        except SQLAlchemyError as e:
            logger.error("Ошибка при добавлении записи {}", e)
            await self._session.rollback()

    async def add_many(
        self,
        instances: List[BaseModel],
        exclude: set[str] | None = None,
    ) -> list[M]:
        values_list = [
            item.model_dump(exclude_unset=True, exclude=exclude)
            for item in instances
        ]
        logger.info(
            "Добавление нескольких записей {}. Количество: {}",
            self.model.__name__,
            len(values_list),
        )
        try:
            new_instances = [
                self.model(**values) for values in values_list
            ]
            self._session.add_all(new_instances)
            await self._session.flush()
            logger.info(
                "Успешно добавлено {} записей.", len(new_instances)
            )
            return new_instances
        except SQLAlchemyError as e:
            logger.error(
                "Ошибка при добавлении нескольких записей: {}", e
            )
            raise

    async def update(
        self, filters: BaseModel, values: BaseModel
    ) -> int:
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            "Обновление записей {} по фильтру: {} с параметрами: {}",
            self.model.__name__,
            filter_dict,
            values_dict,
        )
        try:
            query = (
                sqlalchemy_update(self.model)
                .where(
                    *[
                        getattr(self.model, k) == v
                        for k, v in filter_dict.items()
                    ]
                )
                .values(**values_dict)
                .execution_options(synchronize_session="fetch")
            )
            result = await self._session.execute(query)
            await self._session.flush()
            logger.info("Обновлено {} записей.", result.rowcount)
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error("Ошибка при обновлении записей: {}", e)
            raise

    async def delete(self, filters: BaseModel) -> int:
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            "Удаление записей {} по фильтру: {}",
            self.model.__name__,
            filter_dict,
        )
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError(
                "Нужен хотя бы один фильтр для удаления."
            )
        try:
            query = sqlalchemy_delete(self.model).filter_by(
                **filter_dict
            )
            result = await self._session.execute(query)
            await self._session.flush()
            logger.info("Удалено {} записей.", result.rowcount)
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error("Ошибка при удалении записей: {}", e)
            raise
