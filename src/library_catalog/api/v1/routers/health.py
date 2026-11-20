from fastapi import APIRouter
from sqlalchemy import text

from library_catalog.api.dependencies import DbSessionDep
from library_catalog.api.v1.schemas.common import HealthCheckResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Проверить состояние сервиса и работу БД",
)
async def health_check(db: DbSessionDep):
    """
    Проверить здоровье сервиса.

    Проверяет:
    - Сервис запущен
    - Подключение к БД работает
    """
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthCheckResponse(
        status="healthy",
        database=db_status,
    )
