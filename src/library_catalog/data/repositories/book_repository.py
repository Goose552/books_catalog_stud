from sqlalchemy import select

from library_catalog.data.models.book import Book
from library_catalog.data.repositories.base import BaseRepository


class BookRepository(BaseRepository[Book]):
    model = Book

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
        exact = {
            "genre": genre,
            "year": year,
            "available": available,
        }
        exact = {k: v for k, v in exact.items() if v is not None}

        query = select(Book).filter_by(**exact)

        if title is not None:
            query = query.where(Book.title.ilike(f"%{title}%"))
        if author is not None:
            query = query.where(Book.author.ilike(f"%{author}%"))

        query = query.order_by(Book.book_id).limit(limit).offset(offset)

        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def find_by_isbn(self, isbn: str) -> Book | None:
        """Найти книгу по ISBN"""
        query = select(self.model).where(Book.isbn.ilike(f"%{isbn}"))
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
        """Подсчитать количество книг по фильтрам"""
        res = await self.find_by_filters(
            title=title, author=author, genre=genre, year=year, available=available
        )
        return len(res)
