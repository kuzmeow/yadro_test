from collections.abc import Generator
from contextlib import asynccontextmanager
from typing import Any

import pytest_asyncio
from dishka import Container
from sqlalchemy import text
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
#  DB session
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
def db_session(dishka_container: Container) -> Generator[Session, Any]:
    """Возвращает сессию SQLAlchemy из DI-контейнера."""
    with dishka_container() as request_container:
        session = request_container.get(Session)
        yield session


# ---------------------------------------------------------------------------
#  DB Temporary Entities Management
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def clear_notification_db_table_after_test(db_session: Session):
    try:
        yield
    finally:
        db_session.execute(text("TRUNCATE TABLE notification RESTART IDENTITY CASCADE;"))
        db_session.commit()


@pytest_asyncio.fixture
async def db_object(db_session: Session):
    """
    Возвращает контекстный менеджер, который создает запись в БД, соотв. переданной ORM модели.
    БЕЗ удаления в конце теста.
    """

    @asynccontextmanager
    async def _temporary_db_object(orm_model):
        db_session.add(orm_model)
        db_session.commit()

        try:
            yield
        finally:
            db_session.commit()

    return _temporary_db_object


@pytest_asyncio.fixture
async def temporary_db_object(db_session: Session):
    """Возвращает контекстный менеджер, который создает запись в БД, соотв. переданной ORM модели на время теста."""

    @asynccontextmanager
    async def _temporary_db_object(orm_model):
        db_session.add(orm_model)
        db_session.commit()

        try:
            yield
        finally:
            try:
                db_session.refresh(orm_model)  # заглушка на случай каскадного удаления объекта (вызовет exc)
                db_session.delete(orm_model)
                db_session.commit()
            except Exception:
                db_session.rollback()  # очищаем состояние сессии, чтобы другие не зависели от возможных exc

    return _temporary_db_object


@pytest_asyncio.fixture
async def temporary_db_objects(db_session: Session):
    """Возвращает контекстный менеджер, который создает записи в БД, объектов из списка ORM моделей на время теста."""

    @asynccontextmanager
    async def _temporary_db_objects(orm_model_list):
        for orm_model in orm_model_list:
            db_session.add(orm_model)
        db_session.commit()

        try:
            yield
        finally:
            for orm_model in orm_model_list:
                db_session.delete(orm_model)
            db_session.commit()

    return _temporary_db_objects
