"""Public discovery of cyclists. Private account fields are never serialized."""
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Path, Query, Request, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.repositories import RedisCache
from community.post_likes import attach_likes, viewer_id
from auth.models import UserModel
from community.bikes import BikeResponse
from community.models import Bike, Post
from community.routes import post_response
from community.schemas import FeedResponse

UserId = Annotated[int, Path(ge=1, le=2147483647)]
Filter = Annotated[str | None, Query(max_length=100)]
router = APIRouter(prefix='/users', tags=['People'], route_class=DishkaRoute)


class PublicUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    city: str | None
    avatar_url: str | None = None
    discipline: str | None
    interests: list[str]


class PeoplePage(BaseModel):
    items: list[PublicUser]
    next_cursor: int | None


class PublicProfile(PublicUser):
    bikes: list[BikeResponse]


def contains(column, value):
    # Treat % and _ as text, not user-controlled SQL LIKE wildcards.
    return column.icontains(value.strip(), autoescape=True)


async def public_user(db: AsyncSession, user_id: int) -> UserModel:
    user = await db.scalar(select(UserModel).where(
        UserModel.id == user_id, UserModel.deleted_at.is_(None)))
    if user is None:
        raise HTTPException(404, 'Пользователь не найден')
    return user


@router.get('')
async def search_people(
    db: FromDishka[AsyncSession], city: Filter = None, discipline: Filter = None,
    brand: Filter = None, model: Filter = None,
    limit: int = Query(20, ge=1, le=100),
    cursor: int | None = Query(None, ge=1, le=2147483647),
) -> PeoplePage:
    query = select(UserModel).where(UserModel.deleted_at.is_(None))
    for column, value in ((UserModel.city, city), (UserModel.discipline, discipline)):
        if value and value.strip():
            query = query.where(contains(column, value))
    bike_filters = [contains(column, value) for column, value in
                    ((Bike.brand, brand), (Bike.model, model)) if value and value.strip()]
    if bike_filters:
        # One EXISTS checks both fields on the same bike and cannot duplicate owners.
        query = query.where(select(Bike.id).where(
            Bike.owner_id == UserModel.id, *bike_filters).exists())
    if cursor is not None:
        query = query.where(UserModel.id > cursor)
    users = list(await db.scalars(query.order_by(UserModel.id).limit(limit + 1)))
    return PeoplePage(items=[PublicUser.model_validate(u) for u in users[:limit]],
                      next_cursor=users[limit - 1].id if len(users) > limit else None)


@router.get('/{user_id}')
async def get_public_profile(user_id: UserId, db: FromDishka[AsyncSession]) -> PublicProfile:
    user = await public_user(db, user_id)
    bikes = await db.scalars(select(Bike).where(Bike.owner_id == user.id).order_by(Bike.id))
    return PublicProfile(**PublicUser.model_validate(user).model_dump(),
                         bikes=[BikeResponse.model_validate(bike) for bike in bikes])


@router.get('/{user_id}/posts')
async def user_posts(user_id: UserId, request: Request, response: Response,
                     db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache],
                     limit: int = Query(20, ge=1, le=100),
                     cursor: int | None = Query(None, ge=1, le=2147483647)) -> FeedResponse:
    user = await public_user(db, user_id)
    query = select(Post).where(Post.author_id == user_id)
    if cursor is not None:
        query = query.where(Post.id < cursor)
    posts = list(await db.scalars(query.order_by(Post.id.desc()).limit(limit + 1)))
    items = [post_response(post, user) for post in posts[:limit]]
    await attach_likes(db, items, await viewer_id(request, db, sessions))
    response.headers["Cache-Control"] = "private, no-store"
    return FeedResponse(items=items,
                        next_cursor=str(posts[limit - 1].id) if len(posts) > limit else None)
