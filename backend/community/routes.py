import base64
import binascii
from datetime import datetime
from typing import Annotated
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Query, Request, UploadFile, Path
from starlette.concurrency import run_in_threadpool
from community.media import MAX_UPLOAD_BYTES, save_photo
from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from auth.current_user import current_user
from auth.models import UserModel
from auth.repositories import RedisCache
from community.models import Post
from community.schemas import AuthorResponse, FeedResponse, PostCreate, PostResponse

PostId = Annotated[int, Path(ge=1, le=2147483647)]

router = APIRouter(prefix='/posts', tags=['Posts'], route_class=DishkaRoute)


def post_response(post: Post, author: UserModel) -> PostResponse:
    return PostResponse(id=post.id, author=AuthorResponse(id=author.id, username=author.username),
                        title=post.title, text=post.text, category=post.category, created_at=post.created_at,
                        photo_url=f"/media/{post.photo_filename}" if post.photo_filename else None)


@router.post('', status_code=201)
async def create_post(dto: PostCreate, request: Request, db: FromDishka[AsyncSession],
                      sessions: FromDishka[RedisCache]) -> PostResponse:
    user = await current_user(request, db, sessions)
    post = Post(author_id=user.id, **dto.model_dump())
    db.add(post)
    await db.flush()
    await db.refresh(post)
    result = post_response(post, user)
    await db.commit()
    return result


@router.get('')
async def feed(db: FromDishka[AsyncSession], limit: int = Query(20, ge=1, le=100),
               cursor: str | None = Query(None, max_length=200)) -> FeedResponse:
    query = select(Post, UserModel).join(UserModel, Post.author_id == UserModel.id).where(UserModel.deleted_at.is_(None))
    if cursor:
        try:
            stamp, ident = base64.b64decode(cursor, altchars=b'-_', validate=True).decode().split('|')
            moment, post_id = datetime.fromisoformat(stamp), int(ident)
            if moment.tzinfo is None or not 0 < post_id < 2**31:
                raise ValueError()
        except (ValueError, UnicodeError, binascii.Error):
            raise HTTPException(422, 'Неверный курсор')
        query = query.where(tuple_(Post.created_at, Post.id) < tuple_(moment, post_id))
    rows = (await db.execute(query.order_by(Post.created_at.desc(), Post.id.desc()).limit(limit + 1))).all()
    items = [post_response(post, user) for post, user in rows[:limit]]
    next_cursor = None
    if len(rows) > limit:
        last = rows[limit - 1][0]
        next_cursor = base64.urlsafe_b64encode(f'{last.created_at.isoformat()}|{last.id}'.encode()).decode()
    return FeedResponse(items=items, next_cursor=next_cursor)


@router.get('/{post_id}')
async def get_post(post_id: PostId, db: FromDishka[AsyncSession]) -> PostResponse:
    row = (await db.execute(select(Post, UserModel).join(UserModel, Post.author_id == UserModel.id)
                           .where(Post.id == post_id, UserModel.deleted_at.is_(None)))).first()
    if row is None:
        raise HTTPException(404, 'Пост не найден')
    return post_response(*row)


@router.put('/{post_id}/photo')
async def upload_photo(post_id: PostId, request: Request, db: FromDishka[AsyncSession],
                       sessions: FromDishka[RedisCache], file: UploadFile) -> PostResponse:
    user = await current_user(request, db, sessions)
    post = await db.scalar(select(Post).where(Post.id == post_id).with_for_update())
    if post is None:
        raise HTTPException(404, 'Пост не найден')
    if post.author_id != user.id:
        raise HTTPException(403, 'Изменять фотографию может только автор')
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, 'Максимальный размер фотографии — 5 МБ')
    directory = request.app.state.upload_dir
    filename = await run_in_threadpool(save_photo, data, directory)
    previous = post.photo_filename
    try:
        post.photo_filename = filename
        result = post_response(post, user)
        await db.commit()
    except BaseException:
        (directory / filename).unlink(missing_ok=True)
        raise
    if previous:
        (directory / previous).unlink(missing_ok=True)
    return result
