from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from library_catalog.data.models.book import Book
from library_catalog.data.repositories.base import BaseRepository


class BookRepository(BaseRepository[Book]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)

    def _apply_filters(
        self,
        query: Select,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
    ) -> Select:
        """Применить фильтры к запросу."""
        exact = {
            "genre": genre,
            "year": year,
            "available": available,
        }
        exact = {k: v for k, v in exact.items() if v is not None}

        query = query.filter_by(**exact)

        if title is not None:
            query = query.where(Book.title.ilike(f"%{title}%"))
        if author is not None:
            query = query.where(Book.author.ilike(f"%{author}%"))
        return query

    async def find_by_filters(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Book]:
        """Поиск книг с фильтрацией."""
        query = self._apply_filters(
            select(Book),
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
        )
        query = query.order_by(Book.book_id).limit(limit).offset(offset)

        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def find_by_isbn(self, isbn: str) -> Book | None:
        """Найти книгу по ISBN"""
        query = select(self.model).where(Book.isbn == isbn)
        res = await self.session.execute(query)
        return res.scalar_one_or_none()

    async def count_by_filters(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
    ) -> int:
        query = self._apply_filters(
            select(func.count()).select_from(Book),
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
        )
        res = await self.session.execute(query)
        return res.scalar_one()
