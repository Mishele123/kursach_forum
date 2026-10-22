import argparse
import asyncio
import random

from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from sqlalchemy import delete, select
from auth.models import UserModel, UserRole
from community.models import Post, Bike
from config import Config
from shared import new_session_maker


USERS_COUNT = 5
POSTS_PER_USER = 3
BIKES_PER_USER = 2
PASSWORD = "TestPassword123"

USERS = [
    ("alice", "alice@example.com", "Самара", "MTB", ["маршруты", "ремонт"]),
    ("bob", "bob@example.com", "Москва", "шоссе", ["скорость", "тренировки"]),
    ("carol", "carol@example.com", "Казань", "BMX", ["трюки", "парк"]),
    ("dave", "dave@example.com", "Новосибирск", "гравий", ["путешествия"]),
    ("eve", "eve@example.com", "Екатеринбург", "MTB", ["лес", "грязь"]),
]

POSTS = [
    ("Первый маршрут к озеру", "Отличная поездка на 40 км, дорога сухая.", "route"),
    ("Замена цепи", "Поставил новую цепь Shimano, работает тихо.", "maintenance"),
    ("Апгрейд вилки", "Поставил RockShox Recon, стало мягче на корнях.", "upgrade"),
    ("Трюки в парке", "Отработал bunny hop и manual.", "tricks"),
    ("Маршрут по лесу", "Лесная петля 25 км, много корней.", "route"),
    ("Смазка подшипников", "Разобрал каретку, смазал, тишина.", "maintenance"),
]

BIKES = [
    ("Trek", "Marlin 7", 2023),
    ("Giant", "Escape 3", 2022),
    ("Specialized", "Rockhopper", 2024),
    ("Cannondale", "Trail 8", 2021),
]


async def seed(force: bool = False) -> None:
    config = Config()
    maker = new_session_maker(config.postgres)
    hasher = PasswordHasher()
    password_hash = hasher.hash(PASSWORD)

    try:
        async with maker() as db:
            existing = await db.scalar(select(UserModel).limit(1))
            if existing and not force:
                print("Данные уже есть, сид пропущен. Используйте --force для пересоздания.")
                return
            if existing and force:
                await db.execute(delete(Bike))
                await db.execute(delete(Post))
                await db.execute(delete(UserModel))
                await db.commit()
                print("Старые данные удалены")

            now = datetime.now(timezone.utc)

            users: list[UserModel] = []
            for username, email, city, discipline, interests in USERS:
                user = UserModel(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    role=UserRole.USER,
                    city=city,
                    discipline=discipline,
                    interests=interests,
                    bio=f"Привет, я {username}. Катаюсь на велосипеде.",
                    created_at=now - timedelta(days=random.randint(1, 30)),
                )
                db.add(user)
                users.append(user)
            await db.flush()
            print(f"Создано пользователей: {len(users)}")

            posts_created = 0
            for user in users:
                for _ in range(POSTS_PER_USER):
                    title, text, category = random.choice(POSTS)
                    db.add(Post(
                        author_id=user.id,
                        title=title,
                        text=text,
                        category=category,
                        created_at=now - timedelta(
                            days=random.randint(0, 20),
                            hours=random.randint(0, 23),
                        ),
                    ))
                    posts_created += 1
            print(f"Создано постов: {posts_created}")

            bikes_created = 0
            for user in users:
                for _ in range(BIKES_PER_USER):
                    brand, model, year = random.choice(BIKES)
                    db.add(Bike(owner_id=user.id, brand=brand, model=model, year=year))
                    bikes_created += 1
            print(f"Создано велосипедов: {bikes_created}")

            await db.commit()

    finally:
        await maker.kw["bind"].dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Удалить старые данные и создать заново")
    args = parser.parse_args()
    asyncio.run(seed(force=args.force))