from datetime import datetime
from typing import Annotated
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Query, Request, Response, Path
from pydantic import BaseModel, ConfigDict, StringConstraints
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.current_user import current_user
from auth.models import UserModel, UserRole
from auth.repositories import RedisCache
from community.models import Comment, Post
from community.routes import PostId
from community.schemas import AuthorResponse

router = APIRouter(prefix='/posts', tags=['Comments'], route_class=DishkaRoute)


class CommentCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=3000)]


class CommentResponse(BaseModel):
    id: int
    post_id: int
    author: AuthorResponse
    text: str
    created_at: datetime


class CommentsPage(BaseModel):
    items: list[CommentResponse]
    next_cursor: int | None


def response(comment: Comment, user: UserModel) -> CommentResponse:
    return CommentResponse(id=comment.id, post_id=comment.post_id,
        author=AuthorResponse(id=user.id, username=user.username, avatar_url=user.avatar_url),
        text=comment.text, created_at=comment.created_at)


async def require_post(db: AsyncSession, post_id: int) -> None:
    exists = await db.scalar(select(Post.id).join(UserModel, Post.author_id == UserModel.id)
                            .where(Post.id == post_id, UserModel.deleted_at.is_(None)))
    if exists is None:
        raise HTTPException(404, 'Публикация не найдена')


@router.post('/{post_id}/comments', status_code=201)
async def create_comment(post_id: PostId, dto: CommentCreate, request: Request,
                         db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache]) -> CommentResponse:
    user = await current_user(request, db, sessions)
    await require_post(db, post_id)
    comment = Comment(post_id=post_id, author_id=user.id, text=dto.text)
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    result = response(comment, user)
    await db.commit()
    return result


@router.get('/{post_id}/comments')
async def comments(post_id: PostId, db: FromDishka[AsyncSession],
                   limit: int = Query(20, ge=1, le=100),
                   cursor: int | None = Query(None, ge=1, le=2147483647)) -> CommentsPage:
    await require_post(db, post_id)
    query = select(Comment, UserModel).join(UserModel, Comment.author_id == UserModel.id).where(
        Comment.post_id == post_id, UserModel.deleted_at.is_(None))
    if cursor is not None:
        query = query.where(Comment.id < cursor)
    rows = (await db.execute(query.order_by(Comment.id.desc()).limit(limit + 1))).all()
    return CommentsPage(items=[response(c, u) for c, u in rows[:limit]],
                        next_cursor=rows[limit - 1][0].id if len(rows) > limit else None)


@router.delete('/{post_id}/comments/{comment_id}/moderation', status_code=204, tags=['Moderation'])
async def moderate_comment(post_id: PostId, comment_id: Annotated[int, Path(ge=1, le=2147483647)],
                           request: Request, db: FromDishka[AsyncSession],
                           sessions: FromDishka[RedisCache]) -> Response:
    actor = await current_user(request, db, sessions)
    if actor.role not in {UserRole.MODERATOR, UserRole.ADMIN}:
        raise HTTPException(403, 'Нужны права модератора')
    comment = await db.scalar(select(Comment).where(Comment.id == comment_id,
                              Comment.post_id == post_id).with_for_update())
    if comment is None:
        raise HTTPException(404, 'Комментарий не найден')
    await db.delete(comment)
    await db.commit()
    return Response(status_code=204)
