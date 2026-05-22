"""Базовая модель SQLAlchemy с автоматическим формированием имени таблицы."""

import re

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Добавляет генерацию имени таблицы из имени класса."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa
        """Преобразовать CamelCase имя класса в snake_case название таблицы.

        :return: Имя таблицы в нижнем регистре.
        """

        name = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", cls.__name__)
        return name.lower()
