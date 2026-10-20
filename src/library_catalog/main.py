import uvicorn
from fastapi import FastAPI

app=FastAPI(
    title="Library catalog API",
    description="REST API Для управления библиотечным каталогом",
    version="1.0.0",    
)

@app.get(
    "/",
    summary="Коневой эндпоинт"
)
async def root():
    """Корневой эндпоинт"""
    return {"message": "Welcome to Library Catalog API"}

@app.get(
    "/health",
    summary="Health check"
)
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)