# velo. — Сообщество велосипедистов

React/TypeScript + FastAPI, PostgreSQL, Redis, SQLAlchemy, Alembic, Dishka и Nginx.

Реализованы регистрация и вход по email, Redis-сессии, редактирование профиля и
имени пользователя, аватар, публикации с фото и форматированием, поиск и категории
в ленте, гараж с фотографиями велосипедов. Интерфейс адаптирован для телефонов.

## Запуск после клонирования или git pull

Запустите Docker Desktop с Linux-контейнерами. Из корня репозитория:

```powershell
git pull
docker compose up -d --build
```

- Сайт: http://localhost:8080
- Swagger API: http://localhost:8001/docs
- Проверка PostgreSQL/Redis: http://localhost:8080/api/health

Backend автоматически применяет миграции и добавляет недостающие примеры.
Создайте собственный аккаунт через интерфейс.

## Демонстрационные публикации

В `demo_data/posts.json` сохранены пять опубликованных примеров; фотографии лежат
в `demo_data/assets/`. Эти файлы входят в Git и Docker-образ, поэтому после
запуска на другом компьютере будут видны те же посты с фото, без внешних ссылок.

Импорт включён в Compose через `VELO_SEED_DEMO=1`. Повторный запуск не создаёт
дубликаты. Оригинальные публикации с тем же содержимым пропускаются. Настоящие
аккаунты и изменённые демонстрационные записи не перезаписываются. Если имя
занято, создаётся отдельное имя с суффиксом. Демо-аккаунты не предназначены для
входа: случайные пароли и отключённый вход. Настоящие email, пароли и сессии
не экспортируются.

Для отключения импорта задайте `VELO_SEED_DEMO=0` в корневом `.env` и пересоздайте
backend. Это не удаляет уже добавленные записи. Новые пользовательские посты
остаются в локальной базе; Git не синхронизирует базы участников команды.

## Данные и остановка

```powershell
docker compose down
docker compose up -d
```

PostgreSQL/Redis сохраняются в Docker volumes, пользовательские фото — в
`uploads/`. Не используйте `down -v` и не удаляйте `uploads/`, если нужны данные.
Эти данные и локальные `.env` исключены из Git.

## Миграции

Единая последовательность в `migrations/versions`:

1. `0001_sprint1` — пользователи, публикации, велосипеды.
2. `0002_bike_photo` — необязательное поле фотографии велосипеда.
3. `0003_demo_keys` — уникальные необязательные маркеры демонстрационных записей.

Новые версии добавляют поля и не удаляют существующие записи. Импорт примеров
в `backend/demo.py` отделён от миграций структуры.

```powershell
docker compose exec backend python -m alembic current
docker compose exec backend python -m alembic heads
docker compose exec backend python -m alembic check
docker compose exec backend python scripts/verify_migrations.py
```

Последняя команда проверяет upgrade, повторный upgrade, downgrade/upgrade,
сохранение записей и импорт примеров на отдельной временной PostgreSQL-базе.
После проверки удаляется только временная база; основная `velo` не изменяется.
Откат миграции удаляет соответствующие поля, а `downgrade base` удаляет таблицы.
Проверяйте откаты только на временной базе.

## Проверки

```powershell
docker compose --profile test run --rm --build tests
```

API-тесты используют только `velo_test` и Redis DB 15. Без тестовых переменных
локальный unittest использует временную SQLite и FakeRedis.

Для браузерной проверки в Windows с установленным Microsoft Edge:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe scripts/verify_ui.py
```

Desktop 1440px и mobile 390px: регистрация, смена имени, аватар, велосипед с фото,
пост с фото, вход, перезагрузка и выход. Скрипт удаляет только свои аккаунты и
файлы. Его `DATABASE_URL` должен указывать на ту же локальную базу, что и сервер.
В Linux установите Chromium: `python -m playwright install --with-deps chromium`.
Канал выбирается через `PLAYWRIGHT_CHANNEL`; результаты — в `test-results/`.

## Локальная разработка

Python 3.14, Node.js 24. PostgreSQL: localhost:15432, Redis: localhost:16379.
Настройки по умолчанию — в `.env.example`.

```powershell
docker compose up -d postgres redis
.venv\Scripts\python.exe -m alembic upgrade head
$env:VELO_SEED_DEMO = "1"
.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --port 8000
```

В другом терминале:

```powershell
cd frontend
npm ci
npm run dev
```

Сайт: http://localhost:3000. Vite проксирует `/api`, `/uploads`, `/demo-assets` на
порт 8000. В `frontend/.env` используйте `VITE_API_URL=/api` либо удалите старую
настройку прямого URL. Не смешивайте localhost и 127.0.0.1 в одной сессии.
Проверка сборки: `npm run build`.

Compose читает корневой `.env`, Python получает настройки из окружения:
`DATABASE_URL`, `REDIS_URL`, `VELO_UPLOAD_DIR`, `CORS_ORIGINS`, `VELO_SEED_DEMO`.
При HTTPS включите `VELO_COOKIE_SECURE=1`. Пароль `velo_local` предназначен для
локального запуска. Для другой среды измените `VELO_POSTGRES_PASSWORD` и URL.

Лайки, комментарии, видео и маркетплейс пока не реализованы.
