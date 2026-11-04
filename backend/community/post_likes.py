"""Batch like summaries for public and authenticated publication responses."""
from fastapi import HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.current_user import current_user
from auth.models import UserModel
from auth.repositories import RedisCache
from community.models import PostLike
from community.schemas import PostResponse


async def viewer_id(request: Request, db: AsyncSession, sessions: RedisCache) -> int | None:
    if not request.cookies.get('session_id'):
        return None
    try:
        return (await current_user(request, db, sessions)).id
    except HTTPException as error:
        if error.status_code in (401, 403):
            return None  # A stale cookie must not prevent public reading.
        raise


async def summaries(db: AsyncSession, post_ids: list[int], user_id: int | None) -> dict[int, tuple[int, bool]]:
    if not post_ids:
        return {}
    rows = await db.execute(select(
        PostLike.post_id, func.count(),
        (func.count().filter(PostLike.user_id == user_id) > 0),
    ).join(UserModel, PostLike.user_id == UserModel.id).where(
        PostLike.post_id.in_(post_ids), UserModel.deleted_at.is_(None),
    ).group_by(PostLike.post_id))
    return {post_id: (count, liked) for post_id, count, liked in rows}


async def attach_likes(db: AsyncSession, items: list[PostResponse], user_id: int | None) -> None:
    stats = await summaries(db, [item.id for item in items], user_id)
    for item in items:
        item.like_count, item.liked_by_me = stats.get(item.id, (0, False))
