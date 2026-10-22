"""Import versioned public examples; schema changes belong to Alembic."""
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select, text
from starlette.concurrency import run_in_threadpool

from auth.password import hash_password
from database import Database
from models import PostRow, UserRow
from posts.post_dto import CreatePostDto

DEMO_DIR = Path(__file__).resolve().parents[1] / "demo_data"


def image_url(filename: str | None) -> str | None:
    if filename is None:
        return None
    if Path(filename).name != filename or not (DEMO_DIR / "assets" / filename).is_file():
        raise ValueError("Missing or invalid bundled image")
    return f"/demo-assets/{filename}"


async def seed_demo(database: Database) -> int:
    data = json.loads((DEMO_DIR / "posts.json").read_text(encoding="utf-8"))
    authors = {author["key"]: author for author in data["authors"]}
    # Validate the complete bundle before writing anything.
    for author in authors.values():
        image_url(author.get("avatar"))
    for post in data["posts"]:
        CreatePostDto.model_validate(post)
        image_url(post.get("photo"))
        if post["author"] not in authors:
            raise ValueError("Unknown demo author")

    created = 0
    async with database.session() as session:
        if database.url.startswith("postgresql"):
            # Serialize simultaneous starts; do not depend on row IDs or a local marker file.
            await session.execute(text("SELECT pg_advisory_xact_lock(829410731)"))
        for post in data["posts"]:
            existing = await session.scalar(select(PostRow.id).where(PostRow.demo_key == post["key"]))
            if existing is not None:
                continue
            # The author's original local posts may already be present: leave them untouched.
            original = await session.scalar(select(PostRow.id).where(
                PostRow.title == post["title"], PostRow.text == post["text"],
                PostRow.category == post["category"],
            ))
            if original is not None:
                continue
            author = authors[post["author"]]
            user = await session.scalar(select(UserRow).where(UserRow.demo_key == author["key"]))
            if user is None:
                username = author["username"]
                suffix = 0
                while await session.scalar(select(UserRow.id).where(UserRow.username_key == username.casefold())) is not None:
                    suffix += 1
                    username = f"{author['username'][:38]}_demo{suffix}"
                now = datetime.now(timezone.utc)
                user = UserRow(
                    demo_key=author["key"], username=username, username_key=username.casefold(),
                    email=None, email_key=None,
                    password_hash=await run_in_threadpool(hash_password, secrets.token_urlsafe(48)),
                    role="USER", is_banned=True, avatar_url=image_url(author.get("avatar")),
                    created_at=now, updated_at=now, last_password_change=now,
                )
                session.add(user)
                await session.flush()
            stamp = datetime.fromisoformat(post["created_at"])
            session.add(PostRow(
                demo_key=post["key"], title=post["title"], text=post["text"],
                category=post["category"], author_id=user.id,
                photo_url=image_url(post.get("photo")), created_at=stamp, updated_at=stamp,
            ))
            await session.flush()
            created += 1
    return created
