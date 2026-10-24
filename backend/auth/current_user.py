from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import UserModel
from auth.repositories import RedisCache
from auth.services.auth_service import is_user_banned


async def current_user(request: Request, db: AsyncSession, sessions: RedisCache) -> UserModel:
    session_id = request.cookies.get('session_id')
    session = await sessions.get_session(session_id) if session_id else None
    if session is None:
        raise HTTPException(401, 'Требуется вход')
    user = await db.get(UserModel, session.user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(401, 'Пользователь недоступен')
    if is_user_banned(user):
        raise HTTPException(403, 'Пользователь заблокирован')
    return user
