"""One-time local operator command: python -m bootstrap_admin USERNAME."""
import asyncio
import sys
from sqlalchemy import select, func, text
from auth.models import UserModel, UserRole
from auth.services.auth_service import is_user_banned
from config import Config
from shared import new_session_maker


async def bootstrap(username: str) -> None:
    maker = new_session_maker(Config().postgres)
    try:
        async with maker() as db:
            # Lock the role table to prevent two simultaneous first-admin grants.
            await db.execute(text('LOCK TABLE users IN SHARE ROW EXCLUSIVE MODE'))
            existing = await db.scalar(select(func.count()).select_from(UserModel).where(UserModel.role == UserRole.ADMIN))
            if existing:
                raise SystemExit('Администратор уже существует. Используйте API управления ролями.')
            user = await db.scalar(select(UserModel).where(UserModel.username == username, UserModel.deleted_at.is_(None)))
            if user is None or is_user_banned(user):
                raise SystemExit('Активный пользователь с таким именем не найден.')
            user.role = UserRole.ADMIN
            await db.commit()
            print(f'Администратор назначен: {user.username}')
    finally:
        await maker.kw['bind'].dispose()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Использование: python -m bootstrap_admin ИМЯ_ПОЛЬЗОВАТЕЛЯ')
    asyncio.run(bootstrap(sys.argv[1]))
