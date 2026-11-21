from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


from library_catalog.api.v1.schemas.types_validate import SafeStr

_REQUIRED_FIELDS = ("title", "author", "year", "genre", "pages", "available")


class BookBase(BaseModel):
    """Базовая схема с общими полями"""

    title: SafeStr = Field(min_length=1, max_length=500)
    author: SafeStr = Field(min_length=1, max_length=300)
    year: int = Field(ge=1000, le=2100)
    genre: SafeStr = Field(min_length=1, max_length=100)
    pages: int = Field(gt=0, le=10_000)

class BookCreate(BookBase):
    """Схема для создания книги."""

    isbn: str | None = Field(None, min_length=10, max_length=20)
    description: SafeStr | None = Field(None, max_length=5000)

    @field_validator("isbn")
    @classmethod
    def validate_isbn_field(cls, v: str | None) -> str | None:
        return validate_isbn(v)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Clean Code",
                    "author": "Robert Martin",
                    "year": 2008,
                    "genre": "Programming",
                    "pages": 464,
                    "isbn": "978-0132350884",
                    "description": "A Handbook of Agile Software Craftsmanship",
                }
            ]
        }
    }


class BookUpdate(BaseModel):
    """Схема для обновления книги (все поля опциональны)."""

    title: SafeStr | None = Field(None, min_length=1, max_length=500)
    author: SafeStr | None = Field(None, min_length=1, max_length=300)
    year: int | None = Field(None, ge=1000, le=2100)
    genre: SafeStr | None = Field(None, min_length=1, max_length=100)
    pages: int | None = Field(None, gt=0, le=10_000)
    available: bool | None = None
    isbn: str | None = Field(None, max_length=20)
    description: SafeStr | None = Field(None, max_length=5000)
    
    @field_validator("isbn")
    @classmethod
    def validate_isbn_field(cls, v: str | None) -> str | None:
        return validate_isbn(v)
    
    @model_validator(mode="after")
    def forbid_null_for_required(self) -> "BookUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        for name in _REQUIRED_FIELDS:
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")

        return self


class ShowBook(BookBase):
    """Схема для отображения книги (response)."""

    book_id: UUID
    available: bool
    isbn: str | None
    description: str | None
    extra: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,  # Для ORM моделей
        "json_schema_extra": {
            "examples": [
                {
                    "book_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Clean Code",
                    "author": "Robert Martin",
                    "year": 2008,
                    "genre": "Programming",
                    "pages": 464,
                    "available": True,
                    "isbn": "978-0132350884",
                    "description": "A Handbook of Agile Software Craftsmanship",
                    "extra": {
                        "cover_url": "https://covers.openlibrary.org/b/id/123-L.jpg",
                        "subjects": ["Computer Science", "Software Engineering"],
                    },
                    "created_at": "2024-01-01T12:00:00",
                    "updated_at": "2024-01-01T12:00:00",
                }
            ]
        },
    }


class BookFilters(BaseModel):
    """Фильтры для поиска книг."""

    title: SafeStr | None = Field(
        None, description="Поиск по названию (частичное совпадение)"
    )
    author: SafeStr | None = Field(
        None, description="Поиск по автору (частичное совпадение)"
    )
    genre: SafeStr | None = Field(None, description="Точное совпадение жанра")
    year: int | None = Field(None, description="Точное совпадение года")
    available: bool | None = Field(None, description="Фильтр по доступности")

def validate_isbn(v: str | None) -> str | None:
    if v is None:
        return v

    clean = v.replace("-", "").replace(" ", "")

    if not clean.replace("X", "").isdigit():
        raise ValueError("ISBN must contain only digits")

    if len(clean) not in (10, 13):
        raise ValueError("ISBN must be 10 or 13 digits")

    return clean.upper()