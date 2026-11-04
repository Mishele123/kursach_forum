from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from auth.current_user import current_user
from auth.models import UserModel
from auth.repositories import RedisCache
from community.models import Post, PostLike
from community.post_likes import summaries
from community.routes import PostId

router = APIRouter(prefix='/posts', tags=['Likes'], route_class=DishkaRoute)


class LikeResponse(BaseModel):
    post_id: int
    like_count: int
    liked_by_me: bool


async def set_like(post_id: int, user_id: int, enabled: bool, db: AsyncSession) -> LikeResponse:
    # Serialize writes to a publication, including concurrent PUT/DELETE requests.
    post = await db.scalar(select(Post).join(UserModel, Post.author_id == UserModel.id).where(
        Post.id == post_id, UserModel.deleted_at.is_(None)).with_for_update(of=Post))
    if post is None:
        raise HTTPException(404, 'Публикация не найдена')
    if enabled:
        await db.execute(insert(PostLike).values(post_id=post_id, user_id=user_id)
                         .on_conflict_do_nothing(index_elements=['post_id', 'user_id']))
    else:
        await db.execute(delete(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == user_id))
    count, liked = (await summaries(db, [post_id], user_id)).get(post_id, (0, False))
    await db.commit()
    return LikeResponse(post_id=post_id, like_count=count, liked_by_me=liked)


@router.put('/{post_id}/like')
async def like(post_id: PostId, request: Request, response: Response,
               db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache]) -> LikeResponse:
    user = await current_user(request, db, sessions)
    response.headers['Cache-Control'] = 'private, no-store'
    return await set_like(post_id, user.id, True, db)


@router.delete('/{post_id}/like')
async def unlike(post_id: PostId, request: Request, response: Response,
                 db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache]) -> LikeResponse:
    user = await current_user(request, db, sessions)
    response.headers['Cache-Control'] = 'private, no-store'
    return await set_like(post_id, user.id, False, db)
