📚 Library Catalog

REST API для каталога книг. Позволяет создавать, искать, обновлять и удалять книги, а при создании автоматически обогащает данные из Open Library: обложка, темы, издатель, рейтинг. Если Open Library недоступен, книга всё равно создаётся.

Возможности
CRUD для книг с фильтрацией и пагинацией
Валидация данных (формат ISBN, год, количество страниц)
Проверка уникальности ISBN (409 Conflict при дубликате)
Обогащение данных через Open Library API (retry с экспоненциальным backoff)
Health check с проверкой подключения к БД
Автогенерируемая документация (Swagger UI / ReDoc)
Миграции схемы БД через Alembic
Технологии
Компонент	Технология	Версия	Назначение
Web Framework	FastAPI	0.109+	Быстрый async framework с автодокументацией
ASGI Server	Uvicorn	0.27+	Запуск async приложения
Database	PostgreSQL	16+	Production-ready СУБД
ORM	SQLAlchemy	2.0+	Async работа с БД
Migrations	Alembic	1.13+	Версионирование схемы БД
Validation	Pydantic	2.5+	Валидация через типы
HTTP Client	httpx	0.26+	Async HTTP запросы
Dependencies	Poetry	latest	Управление зависимостями и виртуальным окружением

Python: 3.11+

Архитектура

Проект разделён на слои, каждый отвечает за своё:

src/library_catalog/
├── api/v1/            # Роутеры и Pydantic-схемы
├── core/              # Конфигурация, исключения приложения
├── data/              # Модели SQLAlchemy и репозитории
├── domain/            # Бизнес-логика: сервисы, мапперы
├── external/          # Клиенты внешних API (Open Library)
├── scripts/           # Вспомогательные скрипты
├── utils/             # Утилиты
└── main.py            # Точка входа

Поток запроса: router → service → repository → БД.

Репозитории только работают с данными и не управляют транзакциями
Сервисы содержат бизнес-правила и решают, когда делать commit
Исключения приложения превращаются в HTTP-ответы глобальным обработчиком
Быстрый старт
1. Клонирование и установка зависимостей
bash
git clone <url-репозитория>
cd books_catalog_stud
poetry install
2. Настройка окружения

Скопируйте пример и при необходимости отредактируйте значения:

bash
cp .env.example .env
Переменная	Пример	Описание
ENVIRONMENT	development	Окружение запуска
DEBUG	true	Режим отладки (включает автоперезагрузку при запуске через main.py)
DATABASE_URL	postgresql+asyncpg://postgres:postgres@localhost:5433/library_catalog	Строка подключения к PostgreSQL
API_V1_PREFIX	/api/v1	Префикс API
LOG_LEVEL	INFO	Уровень логирования

PostgreSQL из docker-compose.yml проброшен на порт 5433, поэтому в DATABASE_URL должен быть именно он.

3. Запуск базы данных
bash
docker compose up -d

Поднимется PostgreSQL 16 (library_catalog_db) с базой library_catalog. Данные хранятся в volume postgres_data и сохраняются между перезапусками.

4. Применение миграций
bash
poetry run alembic upgrade head
5. Запуск приложения
bash
poetry run uvicorn library_catalog.main:app --reload

Приложение будет доступно на http://127.0.0.1:8000

Документация API
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
Эндпоинты

Базовый префикс: /api/v1

Книги
Метод	Путь	Описание	Успех
POST	/books/	Создать книгу (с обогащением из Open Library)	201
GET	/books/	Список книг с фильтрами и пагинацией	200
GET	/books/{book_id}	Получить книгу по ID (UUID)	200
PATCH	/books/{book_id}	Частичное обновление (только изменяемые поля)	200
DELETE	/books/{book_id}	Удалить книгу	204
Параметры GET /books/
Параметр	Тип	Описание
title	string	Частичное совпадение, без учёта регистра
author	string	Частичное совпадение, без учёта регистра
genre	string	Точное совпадение
year	int	Точное совпадение
available	bool	Фильтр по доступности
page	int	Номер страницы, начиная с 1
page_size	int	Размер страницы: 1–100, по умолчанию 20

Пример: GET /api/v1/books/?genre=Programming&available=true&page=1&page_size=20

Служебные
Метод	Путь	Описание
GET	/health/	Состояние сервиса и подключения к БД

Ответ: {"status": "healthy", "database": "connected"}. Если БД недоступна, поле database будет "disconnected".

Пример создания книги
bash
curl -X POST http://127.0.0.1:8000/api/v1/books/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert Martin",
    "year": 2008,
    "genre": "Programming",
    "pages": 464,
    "isbn": "978-0132350884",
    "description": "A Handbook of Agile Software Craftsmanship"
  }'
Коды ошибок
Код	Когда
400	Невалидные бизнес-данные (год в будущем, страницы ≤ 0)
404	Книга не найдена
409	Книга с таким ISBN уже существует
422	Ошибка валидации входных данных (например, неверный формат ISBN)
Разработка
bash
poetry run ruff check .     # линтер
poetry run mypy .           # проверка типов
poetry run pytest           # тесты

Создание новой миграции:

bash
poetry run alembic revision --autogenerate -m "описание изменений"
poetry run alembic upgrade head