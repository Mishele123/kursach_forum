from sqlalchemy import select, or_

from database import Database
from models import PostRow, UserRow
from posts.post_entity import Post
from posts.post_dto import PostResponseDto


class PostStorage:
    def __init__(self, database: Database):
        self.database = database

    async def create(self, entity: Post) -> Post:
        async with self.database.session() as session:
            row = PostRow(**entity.model_dump(exclude={"id"}))
            session.add(row)
            await session.flush()
            entity.id = row.id
        return entity

    async def get_by_id(self, post_id: int) -> Post | None:
        async with self.database.session() as session:
            row = await session.get(PostRow, post_id)
            return Post.model_validate(row, from_attributes=True) if row else None

    async def get_all(self, limit: int = 20, offset: int = 0, category: str | None = None, author_id: int | None = None, q: str | None = None) -> list[PostResponseDto]:
        query = select(PostRow, UserRow.username).join(UserRow, UserRow.id == PostRow.author_id)
        if category:
            query = query.where(PostRow.category == category)
        if author_id is not None:
            query = query.where(PostRow.author_id == author_id)
        if q:
            # Escape SQL wildcards: the search box accepts literal text.
            query = query.where(or_(PostRow.title.icontains(q, autoescape=True), PostRow.text.icontains(q, autoescape=True)))
        query = query.order_by(PostRow.created_at.desc(), PostRow.id.desc()).limit(limit).offset(offset)
        async with self.database.session() as session:
            rows = (await session.execute(query)).all()
            return [PostResponseDto(**Post.model_validate(row, from_attributes=True).model_dump(exclude={"updated_at"}), author_username=username) for row, username in rows]
