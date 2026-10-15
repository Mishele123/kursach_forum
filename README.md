# web-forum

Веб-форум с системой аутентификации, разграничением прав доступа и модерацией контента.

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
цифры или `_`) и паролем (8–20 символов). Затем выполните `POST /auth/login`
с теми же данными и `remember_me: true`. Успешные ответы: 201 и 200.
Вход устанавливает cookie `session_id`; сессия хранится в Redis.

Повторная регистрация имени должна вернуть 409, неверный пароль при входе — 401.

## Полностью в Docker

После настройки `.env`:

```bash
docker compose up -d --wait postgres redis
docker compose build backend
docker compose run --rm backend alembic upgrade head
docker compose up -d backend
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

Начальная миграция создаёт таблицу пользователей и тип ролей; следующих функций
форума (темы и сообщения) пока нет. Cookie настроена для локальной разработки
по HTTP; публичное развёртывание требует отдельной настройки.
