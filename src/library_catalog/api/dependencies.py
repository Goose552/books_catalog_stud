from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from library_catalog.core.config import settings
from library_catalog.core.database import get_db
from library_catalog.data.repositories.book_repository import BookRepository
from library_catalog.domain.services.book_service import BookService
from library_catalog.external.openlibrary.client import OpenLibraryClient


@lru_cache
def get_openlibrary_client() -> OpenLibraryClient:
    return OpenLibraryClient(
        base_url=settings.openlibrary_base_url, timeout=settings.openlibrary_timeout
    )


# ========== REPOSITORIES ==========


async def get_book_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BookRepository:
    """
    Создать BookRepository для текущей сессии БД.

    Создается новый экземпляр для каждого запроса.
    """
    return BookRepository(db)


async def get_book_service(
    book_repo: Annotated[BookRepository, Depends(get_book_repository)],
    ol_client: Annotated[OpenLibraryClient, Depends(get_openlibrary_client)],
) -> BookService:
    return BookService(
        book_repository=book_repo,
        openlibrary_client=ol_client,
    )


BookServiceDep = Annotated[BookService, Depends(get_book_service)]
BookRepoDep = Annotated[BookRepository, Depends(get_book_repository)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
