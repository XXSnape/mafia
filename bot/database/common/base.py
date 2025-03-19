from sqlalchemy.orm import declared_attr, DeclarativeBase


class BaseModel(DeclarativeBase):
    """
    Абстрактный класс для работы с моделями.
    """

    __abstract__ = True
    number_output_fields = 3

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Возвращает название таблицы по имени модели.
        """
        return f"{cls.__name__.lower()[:-len('Model')]}s"

    def __repr__(self) -> str:
        """
        Возвращает строку с первыми 3 колонками и значениями.
        """
        cols = [
            f"{field}={getattr(self, field)}"
            for field in self.__table__.columns.keys()[
                : self.number_output_fields
            ]
        ]

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
