from library_catalog.api.v1.schemas.book import ShowBook
from library_catalog.data.models.book import Book


class BookMapper:
    """Маппер для преобразования Book entity в DTO."""

    @staticmethod
    def to_show_book(book: Book) -> ShowBook:
        """
        Преобразовать Book ORM модель в ShowBook DTO.

        Args:
            book: ORM модель из БД
        Returns:
            ShowBook: Pydantic модель для API
        """
        return ShowBook.model_validate(book)

    @staticmethod
    def to_show_books(books: list[Book]) -> list[ShowBook]:
        """Преобразовать список книг."""
        return [ShowBook.model_validate(book) for book in books]
