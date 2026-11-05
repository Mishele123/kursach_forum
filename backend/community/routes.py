import base64
import binascii
from datetime import datetime
from typing import Annotated
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Query, Request, Response, UploadFile, Path, Form, File
from community.media import remove_photo
from community.post_photos import attach_photos, save_batch, MAX_POST_PHOTOS
from sqlalchemy import select, tuple_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from auth.current_user import current_user
from auth.models import UserModel
from auth.repositories import RedisCache
from community.post_likes import attach_likes, viewer_id
from community.models import Post, PostPhoto
from community.schemas import Category, AuthorResponse, FeedResponse, PostCreate, PostResponse, Title, Text

PostId = Annotated[int, Path(ge=1, le=2147483647)]

router = APIRouter(prefix='/posts', tags=['Posts'], route_class=DishkaRoute)


def post_response(post: Post, author: UserModel) -> PostResponse:
    return PostResponse(id=post.id, author=AuthorResponse(id=author.id, username=author.username, avatar_url=author.avatar_url),
                        title=post.title, text=post.text, category=post.category, created_at=post.created_at,
                        photo_url=None)


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
async def feed(request: Request, response: Response, db: FromDishka[AsyncSession],
               sessions: FromDishka[RedisCache], limit: int = Query(20, ge=1, le=100),
               cursor: str | None = Query(None, max_length=200),
               q: str | None = Query(None, max_length=200),
               category: Category | None = Query(None)) -> FeedResponse:
    query = select(Post, UserModel).join(UserModel, Post.author_id == UserModel.id).where(UserModel.deleted_at.is_(None))
    if q and q.strip():
        term = q.strip()
        query = query.where(or_(Post.title.icontains(term, autoescape=True),
                                Post.text.icontains(term, autoescape=True)))
    if category is not None:
        query = query.where(Post.category == category)
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
    await attach_photos(db, items)
    await attach_likes(db, items, await viewer_id(request, db, sessions))
    response.headers["Cache-Control"] = "private, no-store"
    next_cursor = None
    if len(rows) > limit:
        last = rows[limit - 1][0]
        next_cursor = base64.urlsafe_b64encode(f'{last.created_at.isoformat()}|{last.id}'.encode()).decode()
    return FeedResponse(items=items, next_cursor=next_cursor)


@router.post('/with-photos', status_code=201)
async def create_post_with_photos(request: Request, db: FromDishka[AsyncSession],
                                  sessions: FromDishka[RedisCache],
                                  title: Annotated[Title, Form()], text: Annotated[Text, Form()],
                                  category: Annotated[Category, Form()],
                                  files: Annotated[list[UploadFile], File(max_length=MAX_POST_PHOTOS)]) -> PostResponse:
    user = await current_user(request, db, sessions)
    post = Post(author_id=user.id, title=title, text=text, category=category)
    db.add(post)
    await db.flush()
    await db.refresh(post)
    directory = request.app.state.upload_dir
    try:
        filenames = await save_batch(files, directory)
    except BaseException:
        await db.rollback()
        raise
    db.add_all([PostPhoto(post_id=post.id, filename=name) for name in filenames])
    return await finish_photos(post, user, db, directory, filenames)


@router.get('/{post_id}')
async def get_post(post_id: PostId, request: Request, response: Response,
                   db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache]) -> PostResponse:
    row = (await db.execute(select(Post, UserModel).join(UserModel, Post.author_id == UserModel.id)
                           .where(Post.id == post_id, UserModel.deleted_at.is_(None)))).first()
    if row is None:
        raise HTTPException(404, 'Пост не найден')
    result = post_response(*row)
    await attach_photos(db, [result])
    await attach_likes(db, [result], await viewer_id(request, db, sessions))
    response.headers["Cache-Control"] = "private, no-store"
    return result


async def owned_post(post_id, request, db, sessions):
    user = await current_user(request, db, sessions)
    post = await db.scalar(select(Post).where(Post.id == post_id).with_for_update())
    if post is None:
        raise HTTPException(404, 'Пост не найден')
    if post.author_id != user.id:
        raise HTTPException(403, 'Изменять фотографии может только автор')
    return post, user


async def finish_photos(post, user, db, directory, filenames, previous=None):
    try:
        await db.flush()
        result = post_response(post, user)
        await attach_photos(db, [result])
        await attach_likes(db, [result], user.id)
        await db.commit()
    except BaseException:
        await db.rollback()
        for filename in filenames:
            remove_photo(directory, filename)
        raise
    remove_photo(directory, previous)
    return result


@router.put('/{post_id}/photo')
async def upload_photo(post_id: PostId, request: Request, db: FromDishka[AsyncSession],
                       sessions: FromDishka[RedisCache], file: UploadFile) -> PostResponse:
    post, user = await owned_post(post_id, request, db, sessions)
    cover = await db.scalar(select(PostPhoto).where(PostPhoto.post_id == post.id).order_by(PostPhoto.id).limit(1))
    directory = request.app.state.upload_dir
    filenames = await save_batch([file], directory)
    previous = cover.filename if cover else None
    if cover:
        cover.filename = filenames[0]
    else:
        db.add(PostPhoto(post_id=post.id, filename=filenames[0]))
    return await finish_photos(post, user, db, directory, filenames, previous)


@router.post('/{post_id}/photos', status_code=201)
async def upload_photos(post_id: PostId, request: Request, db: FromDishka[AsyncSession],
                        sessions: FromDishka[RedisCache],
                        files: Annotated[list[UploadFile], File(max_length=MAX_POST_PHOTOS)]) -> PostResponse:
    post, user = await owned_post(post_id, request, db, sessions)
    existing = list(await db.scalars(select(PostPhoto.id).where(PostPhoto.post_id == post.id)))
    if len(existing) + len(files) > MAX_POST_PHOTOS:
        raise HTTPException(422, 'В публикации может быть не более 10 фотографий')
    directory = request.app.state.upload_dir
    filenames = await save_batch(files, directory)
    db.add_all([PostPhoto(post_id=post.id, filename=name) for name in filenames])
    return await finish_photos(post, user, db, directory, filenames)
