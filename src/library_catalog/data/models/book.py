import uuid
from datetime import datetime

from sqlalchemy import JSON, VARCHAR, Boolean, DateTime, SmallInteger, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from library_catalog.core.database import Base


class Book(Base):
    """Модель описания книги.

    Используется для описания информации о книге.
    """

    __tablename__ = "books"

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(VARCHAR(500), index=True)
    author: Mapped[str] = mapped_column(
        VARCHAR(300),
        index=True,
    )
    year: Mapped[int] = mapped_column(
        SmallInteger,
        index=True,
    )
    genre: Mapped[str] = mapped_column(VARCHAR(100), index=True)
    pages: Mapped[int] = mapped_column(
        SmallInteger,
    )
    available: Mapped[bool] = mapped_column(Boolean, index=True, default=True)
    isbn: Mapped[str | None] = mapped_column(VARCHAR(20), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    extra: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.book_id}, title='{self.title}')>"
