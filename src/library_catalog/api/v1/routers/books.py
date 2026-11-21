from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from library_catalog.api.dependencies import BookServiceDep
from library_catalog.api.v1.schemas.book import BookCreate, BookUpdate, ShowBook
from library_catalog.api.v1.schemas.common import PaginatedResponse, PaginationParams
from library_catalog.api.v1.schemas.types_validate import SafeStr

router = APIRouter(prefix="/books", tags=["Book"])


@router.post(
    "/",
    response_model=ShowBook,
    status_code=status.HTTP_201_CREATED,
    summary="Создание книги",
    description="Создать новую книгу в каталоге с автоматическим обогащением из Open Library",
)
async def create_book(book_data: BookCreate, service: BookServiceDep):
    """
    Создать новую книгу.

    Автоматически обогащает данные из Open Library API:
    - Обложка книги
    - Темы/subjects
    - Издатель
    - Рейтинг

    Если Open Library недоступен, книга все равно будет создана.
    """
    return await service.create_book(book_data)


@router.get(
    "/",
    response_model=PaginatedResponse[ShowBook],
    summary="Получение списка книг",
    description="Получить список книг с фильтрацией и пагинацией",
)
async def get_books(
    service: BookServiceDep,
    pagination: Annotated[PaginationParams, Depends()],
    title: SafeStr | None = Query(None, description="Поиск по названию"),
    author: SafeStr | None = Query(None, description="Поиск по автору"),
    genre: SafeStr | None = Query(None, description="Фильтр по жанру"),
    year: int | None = Query(None, ge=1000, le=2100, description="Фильтр по году"),
    available: bool | None = Query(None, description="Фильтр по доступности"),
):
    """
    Получить список книг с фильтрацией.
     Поддерживаемые фильтры:
    - title: частичное совпадение (регистронезависимо)
    - author: частичное совпадение (регистронезависимо)
    - genre: точное совпадение
    - year: точное совпадение
    - available: True/False

    Пагинация:
    - page: номер страницы (начиная с 1)
    - page_size: размер страницы (1-100, по умолчанию 20)
    """
    books, total = await service.search_book(
        title=title,
        author=author,
        genre=genre,
        year=year,
        available=available,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return PaginatedResponse.create(books, total, pagination)


@router.get(
    "/{book_id}",
    response_model=ShowBook,
    summary="Получение книги",
    description="Получить информацию о книге по ID",
)
async def get_book(
    book_id: UUID,
    service: BookServiceDep,
):
    """
    Returns:
        ShowBook: Полная информация о книге
    Raises:
        404: Книга не найдена
    """
    return await service.get_book(book_id)


@router.patch(
    "/{book_id}",
    response_model=ShowBook,
    summary="Обновить книгу",
    description="Частичное обновление книги (передаются только изменяемые поля)",
)
async def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    service: BookServiceDep,
):
    """
    Returns:
        ShowBook: Обновленная книга

    Raises:
        404: Книга не найдена
        400: Невалидные данные
    """
    return await service.update_book(book_id, book_data)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить книгу",
    description="Удалить книгу из каталога",
)
async def delete_book(
    book_id: UUID,
    service: BookServiceDep,
):
    """
    Raises:
        404: Книга не найдена
    """
    await service.delete_book(book_id)
