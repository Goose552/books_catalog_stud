import logging
from uuid import UUID
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from library_catalog.api.v1.schemas.book import BookCreate, BookUpdate, ShowBook
from library_catalog.data.repositories.book_repository import BookRepository
from library_catalog.domain.exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    InvalidPagesException,
    InvalidYearException,
    OpenLibraryException,
)
from library_catalog.domain.mappers.book_mapper import BookMapper
from library_catalog.external.openlibrary.client import OpenLibraryClient

logger = logging.getLogger(__name__)


class BookService:
    """
    Сервис для работы с книгами

    Содержит всю бизнес-логику приложения.
    """

    def __init__(
        self,
        book_repository: BookRepository,
        openlibrary_client: OpenLibraryClient,
    ):
        self.book_repo = book_repository
        self.ol_client = openlibrary_client

    async def create_book(self, book_data: BookCreate) -> ShowBook:
        """
        Создать новую книгу с обогащением из Open Library.

        Бизнес-правила:
        - Год не в будущем
        - Страницы > 0
        - ISBN уникален (если указан)

        Args:
            book_data: Данные для создания

        Returns:
            ShowBook: Созданная книга

        Raises:
            InvalidYearException: Если год невалиден
            InvalidPagesException: Если страницы <= 0
            BookAlreadyExistsException: Если ISBN уже существует
        """

        self._validate_book_data(book_data)

        if book_data.isbn:
            existing = await self.book_repo.find_by_isbn(book_data.isbn)
            if existing:
                raise BookAlreadyExistsException(book_data.isbn)

        # 3. Обогощение данными
        extra = await self._enrich_book_data(book_data)

        # 4. Содание записи
        try:
            book = await self.book_repo.create(
                title=book_data.title,
                author=book_data.author,
                year=book_data.year,
                genre=book_data.genre,
                pages=book_data.pages,
                isbn=book_data.isbn,
                description=book_data.description,
                extra=extra,
            )
            await self.book_repo.session.commit()
        except IntegrityError as e:
            await self.book_repo.session.rollback()
            raise BookAlreadyExistsException(book_data.isbn or "") from e
        return BookMapper.to_show_book(book)

    async def get_book(self, book_id: UUID) -> ShowBook:
        """
        Получить книгу по ID.

        Raises:
            BookNotFoundException: Если книга не найдена
        """
        book = await self.book_repo.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(book_id)
        return BookMapper.to_show_book(book)

    async def update_book(
    self,
    book_id: UUID,
    book_data: BookUpdate,
    ) -> ShowBook:
        """
        Обновить книгу.
    
        Обновляются только переданные поля.
    
        Returns:
            ShowBook: измененная книга
    
        Raises:
            BookNotFoundException: если книга не найдена
            BookAlreadyExistsException: если ISBN занят другой книгой
        """
        if book_data.year is not None:
            self._validate_year(book_data.year)
        if book_data.pages is not None:
            self._validate_pages(book_data.pages)
    
        current = await self.get_book(book_id)  # 404, если книги нет
    
        changes = book_data.model_dump(exclude_unset=True)
    
        new_isbn = changes.get("isbn")
        if new_isbn and new_isbn != current.isbn:
            existing = await self.book_repo.find_by_isbn(new_isbn)
            if existing and existing.book_id != book_id:
                raise BookAlreadyExistsException(new_isbn)
    
        try:
            updated = await self.book_repo.update(book_id, **changes)
            if updated is None:
                raise BookNotFoundException(book_id)
            await self.book_repo.session.commit()
        except IntegrityError as e:
            await self.book_repo.session.rollback()
            raise BookAlreadyExistsException(new_isbn or "") from e
    
        return BookMapper.to_show_book(updated)

    async def delete_book(self, book_id: UUID) -> None:
        """
        Удалить книгу.

        Raises:
            BookNotFoundException: Если книга не найдена
        """
        deleted = await self.book_repo.delete(book_id)
        if not deleted:
            raise BookNotFoundException(book_id)
        await self.book_repo.session.commit()

    async def search_book(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ShowBook], int]:
        """
        Поиск книг с фильтрацией и пагинацией.

        Returns:
            tuple: (список книг, общее количество)
        """
        books = await self.book_repo.find_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
            limit=limit,
            offset=offset,
        )

        total = await self.book_repo.count_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
        )

        return BookMapper.to_show_books(books), total

    def _validate_book_data(self, data: BookCreate) -> None:
        """Валидация бизнес-правил для новой книги."""
        self._validate_year(data.year)
        self._validate_pages(data.pages)

    def _validate_year(self, year: int) -> None:
        """Проверить что год валиден."""
        

        current_year = datetime.now().year
        if year < 1000 or year > current_year:
            raise InvalidYearException(year)

    def _validate_pages(self, pages: int) -> None:
        """Проверить что количество страниц валидно."""
        if pages <= 0:
            raise InvalidPagesException(pages)

    async def _enrich_book_data(self, book_data: BookCreate) -> dict | None:
        """
        Обогатить данные книги из Open Library.

        Не выбрасывает исключение если API недоступен.
        """
        try:
            extra = await self.ol_client.enrich(
                title=book_data.title,
                author=book_data.author,
                isbn=book_data.isbn,
            )
            return extra if extra else None
        except OpenLibraryException:
            # Логируем но не прерываем создание книги
            logger.warning(
                "Failed to enrich book data from Open Library",
                extra={"title": book_data.title, "author": book_data.author},
                exc_info=True,
            )
            return None
