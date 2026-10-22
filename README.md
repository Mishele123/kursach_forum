# velo. — Сообщество велосипедистов

Веб-приложение для обмена велосипедными историями, маршрутами и опытом. Реализованы пять пользовательских историй первого спринта. Интерфейс — на русском языке, с адаптацией для компьютеров и телефонов.

## Возможности Sprint 1

| История | Реализованная возможность |
| --- | --- |
| US1 | Регистрация по email, уникальность email/имени, вход, серверная сессия, безопасное хранение пароля, выход |
| US2 | Просмотр и изменение своего города, дисциплины, интересов и описания; изоляция аккаунтов |
| US3 | Заголовок, текст, категория и одна необязательная фотография; жирный текст и курсив; проверки данных и изображения |
| US4 | Общая лента, автор, категория, фотография, отдельная запись, загрузка следующей порции, поиск и фильтрация |
| US5 | Добавление велосипеда с брендом, моделью и годом; личный гараж и отображение в профиле |

Лайки, комментарии, видео и маркетплейс относятся к дальнейшему развитию продукта.

## Быстрый запуск через Docker

Установите и запустите Docker Desktop с Linux-контейнерами. В терминале перейдите **в корень репозитория `kursach_forum`**, где находится `compose.yaml`, затем выполните:

```powershell
docker compose up -d --build
```

Первая сборка загружает образы и зависимости. Сервер автоматически применяет миграции, после готовности PostgreSQL и Redis запускается приложение.

| Адрес | Назначение |
| --- | --- |
| http://localhost:8080 | Интерфейс VELO через Nginx |
| http://localhost:8001/docs | Документация API |
| http://localhost:8080/api/health | Проверка PostgreSQL и Redis |

Зарегистрируйте аккаунт через интерфейс. Используйте одно имя хоста: `localhost` либо `127.0.0.1`.

Просмотр состояния и журналов:

```powershell
docker compose ps
docker compose logs --tail 100 backend
```

Остановка без удаления данных:

```powershell
docker compose down
```

PostgreSQL и Redis сохраняются в Docker volumes `postgres_data` и `redis_data`. Изображения сохраняются в локальной папке `uploads`, подключённой к серверу. Не удаляйте volumes, если данные нужны.

## Разработка без сборки приложений в Docker

Потребуются Python 3.14, Node.js 24 и npm. PostgreSQL и Redis можно запустить отдельно:

```powershell
docker compose up -d postgres redis
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --port 8000
```

В другом терминале из корня репозитория:

```powershell
cd frontend
npm ci
npm run dev
```

Откройте http://localhost:3000. Vite проксирует `/api` и `/uploads` на API с портом 8000. Это отдельный режим разработки; Docker-вариант доступен на 8080, его API — на 8001.

Внешние порты сервисов специально отличаются от стандартных, чтобы не мешать другим проектам:

- PostgreSQL: `127.0.0.1:15432` → контейнер `postgres:5432`.
- Redis: `127.0.0.1:16379` → контейнер `redis:6379`.

## Настройки

Переменные окружения для запуска Python:

| Переменная | Значение по умолчанию вне Docker |
| --- | --- |
| `DATABASE_URL` | `postgresql+asyncpg://velo:velo_local@localhost:15432/velo` |
| `REDIS_URL` | `redis://localhost:16379/0` |
| `VELO_UPLOAD_DIR` | `<проект>/uploads` |
| `VELO_COOKIE_SECURE` | `0`; значение `1` включает cookie только для HTTPS |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` |
| `VITE_API_URL` | `/api`, определяется при сборке клиента |

Файл `.env.example` содержит пример. Python автоматически не читает `.env`; в PowerShell задавайте нужные значения через `$env:DATABASE_URL` и `$env:REDIS_URL`. Docker Compose читает `.env` автоматически. Внутри Compose адреса PostgreSQL и Redis уже настроены на имена сервисов.

Пароль `velo_local` предназначен для локального учебного запуска. Для другой среды задайте `VELO_POSTGRES_PASSWORD`, используйте пароль, пригодный для строки подключения, и обновите `DATABASE_URL` локальных инструментов. При HTTPS включите `VELO_COOKIE_SECURE=1`.

## Миграции и прежние локальные данные

Изменения схемы находятся в `migrations/versions`. Миграции не удаляют старую SQLite-базу.

```powershell
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m alembic check
```

Для однократного переноса данных предыдущей версии в **пустую** PostgreSQL-базу:

```powershell
.venv\Scripts\python.exe scripts/import_legacy_sqlite.py
```

Скрипт читает `data/velo.sqlite3` в режиме только чтения, переносит аккаунты, публикации и велосипеды с прежними ID, обновляет последовательности PostgreSQL и отказывается изменять непустую целевую базу. Исходный файл и изображения остаются на месте. После переноса войдите в аккаунт заново: старые SQLite-сессии не переносятся в Redis.

## Проверка API на PostgreSQL и Redis

Сервисы тестирования используют отдельную базу **`velo_test`** и Redis **DB 15**, а не пользовательские данные:

```powershell
docker compose --profile test run --rm --build tests
```

Набор содержит 15 интеграционных тестов: регистрация и дубликаты, вход и Argon2, права доступа, изоляция аккаунтов, валидация велосипедов/публикаций, пагинация, поиск и фильтры, изображения, блокировка аккаунта, TTL, выход и сохранение данных после повторного создания приложения.

Локальный запуск того же набора на настоящих сервисах:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:VELO_TEST_DATABASE_URL = "postgresql+asyncpg://velo:velo_local@localhost:15432/velo_test"
$env:VELO_TEST_REDIS_URL = "redis://localhost:16379/15"
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Если тестовые переменные не заданы, тесты используют временную SQLite-базу через SQLAlchemy и FakeRedis. Такой режим проверяет API, но не заменяет проверку PostgreSQL/Redis в Docker. Перед следующим офлайн-запуском в том же терминале удалите тестовые переменные из окружения.

## Проверка интерфейса в браузере

Сначала запустите полный стек на порту 8080. Для Windows с установленным Microsoft Edge:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe scripts/verify_ui.py
```

Скрипт проходит регистрацию, изменение профиля, добавление велосипеда, публикацию с фото, просмотр записи, вход, сохранение сессии после перезагрузки и выход на ширинах **1440 и 390 пикселей**. После проверки он удаляет только созданные им аккаунты и изображения. `DATABASE_URL` скрипта должен указывать на ту же локальную PostgreSQL-базу, что и приложение. Для другого адреса интерфейса задайте `VELO_UI_URL`.

В Linux предварительно установите Chromium командой `python -m playwright install --with-deps chromium`. Канал браузера задаётся через `PLAYWRIGHT_CHANNEL`. Скриншоты записываются в `test-results/` и исключены из Git.

Проверка TypeScript и production-сборки:

```powershell
cd frontend
npm run build
```

## Основные API

| Метод | Путь | Назначение |
| --- | --- | --- |
| POST | `/auth/register` | Регистрация: `username`, `email`, `password` |
| POST | `/auth/login` | Вход: `email` или `username`, `password` |
| POST | `/auth/logout` | Отзыв текущей сессии |
| GET / PUT | `/auth/me` | Собственный профиль |
| GET | `/posts` | `limit`, `offset`, `category`, `author_id`, `q` |
| POST | `/posts` | `title`, `text`, `category`, необязательный `photo_url` |
| GET | `/posts/{id}` | Просмотр записи |
| POST | `/uploads` | Multipart-форма с одним полем `file` |
| GET | `/uploads/info` | Ограничения изображений |
| POST | `/bikes` | `brand`, `model`, `year` |
| GET | `/bikes/my-bikes` | Велосипеды текущего пользователя |

Через Nginx методы доступны с префиксом `/api`. Для внешних клиентов API поддерживает `Authorization: Bearer <токен сессии>`. JWT не используется.

Изображения: JPG, PNG, GIF, WEBP, не более 5 МиБ. Проверяются расширение, MIME, сигнатура и целостность изображения через Pillow. К посту можно прикрепить только существующее изображение, загруженное его автором.

## Структура

```text
backend/
  auth/               # Аккаунты, профили, пароли, Redis-сессии
  bikes/              # Велосипеды
  posts/              # Публикации и SQL-пагинация
  shared/             # Загрузка и проверка изображений
  database.py         # AsyncEngine и AsyncSession
  models.py           # Реляционные модели SQLAlchemy
  ioc.py              # Контейнер Dishka
  main.py             # FastAPI и жизненный цикл ресурсов
frontend/
  src/                # React/TypeScript
  nginx.conf          # SPA и проксирование API
  Dockerfile          # Сборка клиента и Nginx
migrations/           # Версионирование схемы Alembic
tests/                # Проверки API
scripts/              # Импорт старых данных и браузерная проверка
compose.yaml          # PostgreSQL, Redis, FastAPI, Nginx и тесты
```

Локальные `.env`, SQLite-файлы предыдущей версии, `uploads`, `.venv`, `node_modules`, `dist` и результаты тестов исключены из Git. `package-lock.json`, исходники, миграции и конфигурация запуска сохраняются в репозитории.
