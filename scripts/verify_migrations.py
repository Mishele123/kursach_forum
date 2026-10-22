"""Exercise Alembic and demo import only in a disposable PostgreSQL database."""
import asyncio
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from database import Database
from demo import seed_demo


async def execute(url, statement, parameters=None, autocommit=False):
    options = {"isolation_level": "AUTOCOMMIT"} if autocommit else {}
    engine = create_async_engine(url, **options)
    try:
        async with engine.begin() as connection:
            result = await connection.execute(text(statement), parameters or {})
            return result.scalar() if result.returns_rows else None
    finally:
        await engine.dispose()


def run():
    source = make_url(os.environ.get("DATABASE_URL", "postgresql+asyncpg://velo:velo_local@localhost:15432/velo"))
    if source.drivername != "postgresql+asyncpg":
        raise RuntimeError("This verification requires PostgreSQL with asyncpg")
    name = "velo_migration_check_" + uuid.uuid4().hex[:12]
    # The sole database created/dropped below is this fixed-prefix random name.
    target = source.set(database=name)
    admin = source.set(database="postgres")
    target_string = target.render_as_string(hide_password=False)
    env = {**os.environ, "DATABASE_URL": target_string, "VELO_SEED_DEMO": "0"}

    def sql(statement, parameters=None):
        return asyncio.run(execute(target, statement, parameters))

    def migrate(*args):
        subprocess.run([sys.executable, "-m", "alembic", *args], cwd=ROOT, env=env, check=True)
        print("PASS: alembic " + " ".join(args), flush=True)

    def counts(users=1, posts=1):
        for table, expected in [("users", users), ("posts", posts), ("bikes", 1)]:
            actual = sql("SELECT COUNT(*) FROM " + table)
            assert actual == expected, (table, actual, expected)
        assert sql("SELECT title FROM posts WHERE id=1") == "Preserve this post"

    async def demo_twice():
        database = Database(target_string)
        try:
            assert await seed_demo(database) == 5
            assert await seed_demo(database) == 0
        finally:
            await database.close()

    created = False
    try:
        asyncio.run(execute(admin, "CREATE DATABASE " + name, autocommit=True))
        created = True
        migrate("upgrade", "0001_sprint1")
        now = datetime.now(timezone.utc)
        sql("INSERT INTO users (id,username,username_key,password_hash,role,is_banned,created_at,updated_at,last_password_change) VALUES (1,'migration_check','migration_check','test-only','USER',false,:now,:now,:now)", {"now": now})
        sql("INSERT INTO posts (id,title,text,category,author_id,created_at,updated_at) VALUES (1,'Preserve this post','Migration check','route',1,:now,:now)", {"now": now})
        sql("INSERT INTO bikes (id,brand,model,year,user_id,created_at) VALUES (1,'Trek','Migration check',2023,1,:now)", {"now": now})
        # Keep sequences in sync after inserting explicit IDs in the fixture.
        for table in ("users", "posts", "bikes"):
            sql(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), 1, true)")
        migrate("upgrade", "head")
        counts()
        assert sql("SELECT photo_url FROM bikes WHERE id=1") is None
        migrate("upgrade", "head")
        migrate("check")
        asyncio.run(demo_twice())
        counts(users=2, posts=6)
        print("PASS: examples imported once; original rows preserved", flush=True)
        migrate("downgrade", "0002_bike_photo")
        counts(users=2, posts=6)
        migrate("upgrade", "head")
        counts(users=2, posts=6)
        # Downgrading marker columns must not duplicate the surviving examples.
        async def reseed():
            database = Database(target_string)
            try:
                assert await seed_demo(database) == 0
            finally:
                await database.close()
        asyncio.run(reseed())
        migrate("downgrade", "0001_sprint1")
        counts(users=2, posts=6)
        migrate("upgrade", "head")
        counts(users=2, posts=6)
        migrate("check")
        migrate("downgrade", "base")
        assert sql("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('users','posts','bikes')") == 0
        migrate("upgrade", "head")
        migrate("check")
        assert sql("SELECT COUNT(*) FROM posts") == 0
        asyncio.run(demo_twice())
        assert sql("SELECT COUNT(*) FROM posts") == 5
        print("ALL MIGRATION AND FRESH-DATABASE DEMO CHECKS PASSED", flush=True)
    finally:
        if created:
            asyncio.run(execute(admin, "DROP DATABASE " + name, autocommit=True))
            print("Temporary database removed; application database untouched", flush=True)


if __name__ == "__main__":
    run()
