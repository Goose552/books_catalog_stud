from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, insert, inspect, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.library_catalog.core.database import Base

ModelVar = TypeVar("ModelVar", bound=Base)


class BaseRepository(Generic[ModelVar]):
    def __init__(self, session: AsyncSession, model: type[ModelVar]):
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> ModelVar:
        """Создать запись в таблице"""

        add_data_stmt = insert(self.model).values(**kwargs).returning(self.model)
        result = await self.session.execute(add_data_stmt)
        return result.scalar_one()

    async def get_by_id(self, id: UUID) -> ModelVar | None:
        """Получения объекта по ID"""

        return await self.session.get(self.model, id)

    async def update(self, id: UUID, **kwargs) -> ModelVar | None:
        """Изменение данных по ID"""

        pk = inspect(self.model).primary_key[0]  # колонка первичного ключа
        update_data_stmt = (
            update(self.model).where(pk == id).values(**kwargs).returning(self.model)
        )
        result = await self.session.execute(update_data_stmt)
        return result.scalar_one_or_none()

    async def delete(self, id: UUID) -> bool:
        """Удалить запись"""

        pk = inspect(self.model).primary_key[0]
        delete_data_stmt = delete(self.model).where(pk == id)
        res = await self.session.execute(delete_data_stmt)
        return res.rowcount > 0

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 10,
    ) -> list[ModelVar]:
        """Поиск книг с фильтрацией"""
        pk = inspect(self.model).primary_key[0]
        query = select(self.model)
        query = query.order_by(pk).limit(limit).offset(offset)
        res = await self.session.execute(query)
        return list(res.scalars().all())
