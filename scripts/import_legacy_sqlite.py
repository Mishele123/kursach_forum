"""Import the previous local SQLite database into an empty PostgreSQL schema."""
import argparse
import asyncio
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from sqlalchemy import select, func, text
from database import Database
from models import UserRow, PostRow, BikeRow
from auth.user_entity import User
from posts.post_entity import Post
from bikes.bike_entity import Bike


async def migrate(source: Path):
    database = Database()
    if not database.url.startswith("postgresql"):
        raise RuntimeError("The destination must be PostgreSQL")
    if not source.is_file():
        raise RuntimeError("The legacy SQLite file does not exist")
    legacy = sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        async with database.session() as session:
            for model in [UserRow, PostRow, BikeRow]:
                if await session.scalar(select(func.count()).select_from(model)):
                    raise RuntimeError("Destination is not empty; no records were imported")
            counts = {}
            for table, entity_type, row_type in [("users", User, UserRow), ("posts", Post, PostRow), ("bikes", Bike, BikeRow)]:
                count = 0
                for (payload,) in legacy.execute(f"SELECT data FROM {table} ORDER BY id"):
                    entity = entity_type.model_validate_json(payload)
                    values = entity.model_dump()
                    if table == "users":
                        values.update(username_key=entity.username.casefold(), email_key=entity.email.casefold() if entity.email else None)
                    session.add(row_type(**values))
                    count += 1
                await session.flush()
                await session.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 1), EXISTS(SELECT 1 FROM {table}))"))
                counts[table] = count
        print("Imported records:", counts)
        print("Original SQLite file is unchanged. Sign in again to create a Redis session.")
    finally:
        legacy.close()
        await database.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "velo.sqlite3")
    asyncio.run(migrate(parser.parse_args().source))
