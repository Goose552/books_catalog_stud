from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from library_catalog.api.v1.routers import books, health
from library_catalog.core.config import settings
from library_catalog.core.database import dispose_engine
from library_catalog.core.exceptions import register_exception_handlers
from library_catalog.core.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager для FastAPI.

    Выполняется при:
    - startup: настройка логирования
    - shutdown: закрытие подключений к БД
    """
    setup_logging()
    print("🚀 Application started")

    yield

    # Shutdown
    await dispose_engine()
    print("👋 Application stopped")


app = FastAPI(
    title="Library catalog API",
    description="REST API Для управления библиотечным каталогом",
    version="1.0.0",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


app.include_router(
    books.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    health.router,
    prefix=settings.api_v1_prefix,
)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "Welcome to Library Catalog API",
        "docs": settings.docs_url,
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
