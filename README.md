# 🚴 Cycling Social Network API

Социальная сеть для велосипедистов - Backend API для Sprint 1

## 📋 О проекте

Backend API для социальной сети велосипедистов, реализующий функциональность первого спринта:
- Регистрация и аутентификация пользователей
- Управление профилем
- Создание и просмотр публикаций
- Добавление велосипедов

## 🛠️ Технологии

- **Python 3.14**
- **FastAPI** - современный веб-фреймворк
- **Uvicorn** - ASGI сервер
- **Dishka** - Dependency Injection
- **Pydantic** - валидация данных
- **Clean Architecture** - архитектурный подход

## 📁 Структура проекта

```
kursach_forum/
├── backend/                 # Backend код
│   ├── auth/               # Модуль аутентификации
│   │   ├── http.py        # HTTP endpoints
│   │   ├── user_entity.py # Доменная модель
│   │   ├── user_dto.py    # Data Transfer Objects
│   │   ├── user_interactor.py # Бизнес-логика
│   │   ├── user_interfaces.py # Интерфейсы репозиториев
│   │   ├── in_memory.py   # In-memory хранилище
│   │   └── user_mapper.py # Маппинг DTO <-> Entity
│   ├── posts/             # Модуль публикаций
│   ├── bikes/             # Модуль велосипедов
│   ├── ioc.py             # Dependency Injection контейнер
│   └── main.py            # FastAPI приложение
├── simple_test.py          # Простой тест API
├── full_test.py            # Полный тест всех endpoints
├── test_browser.html       # HTML интерфейс для тестирования
├── TESTING.md              # Подробная документация по тестированию
├── requirements.txt        # Python зависимости
└── README.md               # Этот файл
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```powershell
pip install -r requirements.txt
```

### 2. Запуск сервера

```powershell
cd backend
python -m uvicorn main:get_app --host 0.0.0.0 --port 8000 --reload
```

Сервер запустится на `http://localhost:8000`

### 3. Просмотр API документации

Откройте в браузере:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root page**: http://localhost:8000/

## 📚 API Endpoints

### 👤 Аутентификация и профиль

```http
POST   /auth/register      # Регистрация пользователя (US1)
POST   /auth/login         # Вход в систему (US1)
GET    /auth/me            # Получить профиль (US2)
PUT    /auth/me            # Обновить профиль (US2)
```

### 📝 Публикации

```http
POST   /posts              # Создать публикацию (US3)
GET    /posts              # Получить ленту (US4)
GET    /posts/{id}         # Получить публикацию по ID
```

### 🚲 Велосипеды

```http
POST   /bikes              # Добавить велосипед (US5)
GET    /bikes/my-bikes     # Получить мои велосипеды (US5)
```

## 🧪 Тестирование

### Вариант 1: Простой тест

```powershell
python simple_test.py
```

### Вариант 2: Полный тест

```powershell
python full_test.py
```

### Вариант 3: HTML интерфейс

Откройте `test_browser.html` в браузере

### Вариант 4: Swagger UI

Откройте http://localhost:8000/docs и тестируйте API в интерактивном режиме

## 📖 Подробная документация

Смотрите [TESTING.md](TESTING.md) для подробной информации о:
- Запуске и тестировании API
- Примерах запросов и ответов
- Архитектуре проекта
- Troubleshooting

## ✅ Реализованные User Stories (Sprint 1)

- ✅ **US1**: Регистрация и аутентификация пользователей
- ✅ **US2**: Редактирование профиля пользователя
- ✅ **US3**: Создание публикаций
- ✅ **US4**: Просмотр ленты публикаций с пагинацией
- ✅ **US5**: Добавление велосипедов в профиль

## 🏗️ Архитектура

Проект следует принципам **Clean Architecture**:

- **Entities** (user_entity.py) - доменные модели
- **Use Cases** (user_interactor.py) - бизнес-логика
- **Interface Adapters** (user_dto.py, user_mapper.py) - преобразование данных
- **Frameworks** (http.py, main.py) - HTTP endpoints

## 🔧 Конфигурация

### Зависимости (requirements.txt)

```
fastapi==0.141.1
uvicorn==0.53.0
dishka==1.10.1
pydantic==2.13.5
SQLAlchemy==2.0.54
argon2-cffi==25.1.0
```

## 📊 Статус проекта

🟢 **Активная разработка** - Sprint 1 завершен

### Текущие ограничения

- Аутентификация использует hardcoded user_id=1 (JWT будет добавлен позже)
- Пароли не хешируются (bcrypt/argon2 будет добавлен позже)
- Данные хранятся in-memory (PostgreSQL будет добавлена позже)

## 👨‍💻 Разработка

### Добавление нового модуля

1. Создайте папку с модулем (например, `comments/`)
2. Добавьте необходимые файлы:
   - `entity.py` - доменная модель
   - `dto.py` - DTO объекты
   - `storage.py` - репозиторий
   - `http.py` - HTTP endpoints
3. Зарегистрируйте в `ioc.py`
4. Подключите router в `main.py`

## 📞 Поддержка

При возникновении проблем:
1. Проверьте, что сервер запущен
2. Проверьте логи в терминале
3. Посмотрите документацию в TESTING.md
4. Используйте Swagger UI для отладки

---

**Версия**: 1.0.0 (Sprint 1)  
**Последнее обновление**: 06.10.2026
