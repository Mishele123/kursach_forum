# Социальная сеть для велосипедистов

Бэкенд первого спринта: публикации и лента, фотографии, вход по email, профиль и велосипеды.

## Локальный запуск на macOS

Нужны Python 3.14 и запущенный Docker Desktop. Команды выполняются из корня проекта.

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Если `.env` ещё нет, скопируйте `.env.example` в `.env`. Укажите собственные
`POSTGRES_PASSWORD` и `REDIS_PASSWORD`. Для запуска Python на компьютере оставьте
хосты `localhost`. `.env` и `.venv` исключены из Git.
Если порт 5432 уже занят другим PostgreSQL, задайте `POSTGRES_PORT=55432`
в `.env`: этот порт используют и Compose, и локальный Python.

```bash
# Добавить утилиты Docker Desktop в PATH текущего терминала
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

docker compose up -d --wait postgres redis
(cd backend && ../.venv/bin/alembic upgrade head)
python -m uvicorn main:app --app-dir backend --reload
```

Документация API: http://127.0.0.1:8000/docs.

В Swagger выполните `POST /auth/register` с именем (3–50 символов: латиница,
цифры или `_`), email и паролем (8–128 символов). Затем выполните `POST /auth/login`
с email, паролем и `remember_me: true` (без поля username). Успешные ответы: 201 и 200.
Вход устанавливает cookie `session_id`; сессия хранится в Redis.

Повторная регистрация имени должна вернуть 409, неверный пароль при входе — 401.

## Полностью в Docker

После настройки `.env`:

```bash
docker compose up -d --wait postgres redis
docker compose build backend
docker compose run --rm backend alembic upgrade head
docker compose up -d backend
docker compose exec backend python seed.py
```

Compose задаёт адреса `postgres` и `redis` для бэкенда внутри контейнера.
Не запускайте одновременно локальный сервер и контейнер бэкенда на порту 8000.

## Полезные команды

```bash
docker compose ps
(cd backend && ../.venv/bin/alembic current)
docker compose logs --tail=50 postgres redis
```

Локальный сервер останавливается через Ctrl+C, контейнеры — `docker compose stop`.
Данные базы сохраняются в Docker-томе. Изменение пароля PostgreSQL в `.env`
после первого запуска не меняет пароль в существующей базе.

Миграции создают пользователей, посты, поля профиля и велосипеды. Фотографии
хранятся в `uploads/` локально и в отдельном томе при запуске в Docker.
Cookie по умолчанию настроена для локальной разработки по HTTP.

## API и первый спринт

- [Контракт API для фронтенда](docs/API.md): запросы, поля, cookie, ошибки и фотографии.
- [Состояние серверной части спринта](docs/SPRINT_1_BACKEND.md): реализованный объём и сценарий демо.

## Интеграционные тесты

Нужны запущенные PostgreSQL и Redis, а также `.env` для локального подключения.

```bash
python -m pip install -r requirements-dev.txt
python tests/run.py
```

Тесты используют временную отдельную базу и отдельные ключи Redis, после чего
удаляют свои данные. Не запускайте их против внешней базы: тестовый runner
рассчитан на сервисы текущего Docker Compose.

После получения новых коммитов обновите зависимости и примените миграции:

```bash
python -m pip install -r requirements.txt
(cd backend && ../.venv/bin/alembic upgrade head)
```

Новые регистрации требуют email. Ранее созданные записи без email сохраняются,
но вход по username больше не поддерживается. См. контракт API.
