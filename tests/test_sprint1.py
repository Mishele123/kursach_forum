"""Acceptance tests: isolated PostgreSQL/Redis services or offline test adapters."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK_ROOT / "backend"))
TEST_DATA = tempfile.TemporaryDirectory()
os.environ["VELO_UPLOAD_DIR"] = str(Path(TEST_DATA.name) / "uploads")
from fastapi.testclient import TestClient
from main import get_app
from models import UserRow
from sqlalchemy import select
from fakeredis import FakeServer
from fakeredis.aioredis import FakeRedis
from redis.asyncio import Redis
from sqlalchemy.engine import make_url
from auth.session import digest
from datetime import timedelta

class SprintOneTests(unittest.TestCase):
    def setUp(self):
        self.database_url = os.environ.get("VELO_TEST_DATABASE_URL", "sqlite+aiosqlite:///" + str(Path(TEST_DATA.name) / "test.sqlite3"))
        self.redis_url = os.environ.get("VELO_TEST_REDIS_URL")
        if self.database_url.startswith("postgresql") and not make_url(self.database_url).database.endswith("_test"):
            raise RuntimeError("Tests require a dedicated database whose name ends in _test")
        if self.redis_url and not self.redis_url.rstrip("/").endswith("/15"):
            raise RuntimeError("Tests require a dedicated Redis DB 15")
        self.fake_server = FakeServer()
        self.app = get_app(self.database_url, self.redis_client())
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)
        self.client.portal.call(self.app.state.database.reset_test_schema)
        self.client.portal.call(self.app.state.redis.flushdb)
        self.register("alice", "alice@example.com")
        self.register("bob", "bob@example.com")

    def redis_client(self):
        return Redis.from_url(self.redis_url, decode_responses=True) if self.redis_url else FakeRedis(server=self.fake_server, decode_responses=True)

    def user_record(self, username):
        async def read():
            async with self.app.state.database.session() as session:
                return await session.scalar(select(UserRow).where(UserRow.username == username))
        return self.client.portal.call(read)

    def register(self, username, email):
        response = self.client.post("/auth/register", json={"username":username,"email":email,"password":"secret123"})
        self.assertEqual(response.status_code,201,response.text)
        return response.json()

    def login(self, email="alice@example.com"):
        response = self.client.post("/auth/login",json={"email":email,"password":"secret123"})
        self.assertEqual(response.status_code,200,response.text)
        return response.json()["access_token"]

    def post(self, **updates):
        data = {"title":"A morning ride","text":"Forest trails and fresh air.","category":"маршрут"}
        data.update(updates)
        return self.client.post("/posts",json=data)

    def test_registration_validation_and_duplicates(self):
        for data in [{"username":"other","email":"ALICE@example.com","password":"secret123"}, {"username":"ALICE","email":"other@example.com","password":"secret123"}]:
            self.assertEqual(self.client.post("/auth/register",json=data).status_code,409)
        for data in [{"username":"   ","email":"ok@example.com","password":"secret123"},{"username":"valid","email":"invalid","password":"secret123"},{"username":"valid","email":"ok@example.com"}]:
            self.assertEqual(self.client.post("/auth/register",json=data).status_code,422)

    def test_login_cookie_and_password_safety(self):
        self.assertEqual(self.client.post("/auth/login",json={"email":"alice@example.com","password":"wrong"}).status_code,401)
        self.login("ALICE@EXAMPLE.COM")
        response=self.client.get("/auth/me")
        self.assertEqual(response.status_code,200)
        self.assertNotIn("password_hash",response.json())
        user = self.user_record("alice")
        self.assertTrue(user.password_hash.startswith("$argon2"))
        cookie=self.client.cookies.get("velo_session")
        self.assertTrue(cookie)

    def test_anonymous_cannot_write(self):
        self.assertEqual(self.client.get("/auth/me").status_code,401)
        self.assertEqual(self.post().status_code,401)
        self.assertEqual(self.client.post("/bikes",json={"brand":"Trek","model":"Marlin","year":2023}).status_code,401)
        self.assertEqual(self.client.get("/bikes/my-bikes").status_code,401)

    def test_profile_and_bikes_are_isolated(self):
        self.login()
        self.assertEqual(self.client.put("/auth/me",json={"city":"Samara","discipline":"MTB","interests":"Trails","bio":"Hello"}).status_code,200)
        bike=self.client.post("/bikes",json={"brand":"Trek","model":"Marlin 7","year":2023})
        self.assertEqual(bike.status_code,201,bike.text)
        self.assertEqual(len(self.client.get("/bikes/my-bikes").json()),1)
        self.login("bob@example.com")
        self.assertIsNone(self.client.get("/auth/me").json()["city"])
        self.assertEqual(self.client.get("/bikes/my-bikes").json(),[])
        self.client.put("/auth/me",json={"city":"Moscow","id":1})
        self.login()
        self.assertEqual(self.client.get("/auth/me").json()["city"],"Samara")

    def test_post_validation(self):
        self.login()
        for update in [{"title":"  "},{"text":"  "},{"title":"x"*201},{"category":"invalid"},{"photo_url":"https://example.com/no.jpg"}]:
            self.assertIn(self.post(**update).status_code,[400,422])
        self.assertEqual(self.post().status_code,201)

    def test_feed_pagination_categories_and_search(self):
        self.login()
        for i in range(4): self.assertEqual(self.post(title=f"Ride {i}").status_code,201)
        self.post(title="Repair notes",category="обслуживание")
        first=self.client.get("/posts?limit=2").json()
        second=self.client.get("/posts?limit=2&offset=2").json()
        self.assertEqual(len(first),2)
        self.assertFalse(set(p["id"] for p in first)&set(p["id"] for p in second))
        self.assertGreater(first[0]["id"],second[0]["id"])
        self.assertEqual(len(self.client.get("/posts",params={"category":"обслуживание"}).json()),1)
        self.assertEqual(len(self.client.get("/posts",params={"q":"repair"}).json()),1)
        self.assertEqual(self.client.get("/posts/999999").status_code,404)

    def test_upload_validation_and_post_with_photo(self):
        self.login()
        self.assertEqual(self.client.post("/uploads",files={"file":("fake.png",b"hello","image/png")}).status_code,400)
        self.assertEqual(self.client.post("/uploads",files={"file":("bad.svg",b"<svg/>","image/svg+xml")}).status_code,400)
        self.assertEqual(self.client.post("/uploads",files={"file":("big.png",b"x"*(5*1024*1024+1),"image/png")}).status_code,413)
        from PIL import Image
        import io
        buffer = io.BytesIO()
        Image.new("RGB", (2, 2), "green").save(buffer, format="PNG")
        png = buffer.getvalue()
        upload=self.client.post("/uploads",files={"file":("photo.png",png,"image/png")})
        self.assertEqual(upload.status_code,201,upload.text)
        url=upload.json()["url"]
        self.assertEqual(self.client.get(url).status_code,200)
        self.assertEqual(self.post(photo_url=url).status_code,201)
        self.login("bob@example.com")
        self.assertEqual(self.post(photo_url=url).status_code,400)

    def test_logout_and_expiry(self):
        token=self.login()
        self.assertEqual(self.client.post("/auth/logout").status_code,204)
        self.assertEqual(self.client.get("/auth/me",headers={"Authorization":f"Bearer {token}"}).status_code,401)
        uid = self.user_record("alice").id
        expired = self.client.portal.call(self.app.state.sessions.create_access_token, uid, timedelta(seconds=-1))
        self.assertEqual(self.client.get("/auth/me",headers={"Authorization":f"Bearer {expired}"}).status_code,401)

    def test_data_and_session_survive_app_recreation(self):
        token=self.login()
        self.post()
        self.client.post("/bikes",json={"brand":"Trek","model":"Marlin","year":2023})
        with TestClient(get_app(self.database_url, self.redis_client())) as restarted:
            headers={"Authorization":f"Bearer {token}"}
            self.assertEqual(restarted.get("/auth/me",headers=headers).status_code,200)
            self.assertEqual(len(restarted.get("/posts").json()),1)
            self.assertEqual(len(restarted.get("/bikes/my-bikes",headers=headers).json()),1)

    def test_bike_validation(self):
        self.login()
        for change in [{"brand":"  "},{"model":""},{"year":1700},{"year":3000}]:
            data={"brand":"Trek","model":"Marlin","year":2023,**change}
            self.assertEqual(self.client.post("/bikes",json=data).status_code,422)

    def test_session_cookie_flags_and_redis_ttl(self):
        response = self.client.post("/auth/login", json={"email":"alice@example.com", "password":"secret123"})
        cookie = response.headers["set-cookie"].lower()
        self.assertIn("httponly", cookie)
        self.assertIn("samesite=lax", cookie)
        token = response.json()["access_token"]
        key = "velo:session:" + digest(token)
        ttl = self.client.portal.call(self.app.state.redis.ttl, key)
        self.assertGreater(ttl, 604700)
        self.assertLessEqual(ttl, 604800)
        self.client.post("/auth/logout")
        self.assertEqual(self.client.portal.call(self.app.state.redis.exists, key), 0)

    def test_banned_account_session_is_rejected(self):
        from sqlalchemy import update
        self.login()
        async def ban():
            async with self.app.state.database.session() as session:
                await session.execute(update(UserRow).where(UserRow.username == "alice").values(is_banned=True))
        self.client.portal.call(ban)
        self.assertEqual(self.client.get("/auth/me").status_code, 401)
        self.assertEqual(self.post().status_code, 401)
        self.assertEqual(self.client.post("/auth/login",json={"email":"alice@example.com","password":"secret123"}).status_code, 403)

    def test_feed_search_treats_wildcards_as_literal_text(self):
        self.login()
        self.post(title="100% cycling")
        self.post(title="Other route")
        result=self.client.get("/posts",params={"q":"%"}).json()
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]["title"],"100% cycling")

    def test_author_filter_and_pagination_validation(self):
        self.login()
        alice = self.user_record("alice").id
        self.post(title="Alice route")
        self.login("bob@example.com")
        self.post(title="Bob route")
        result=self.client.get("/posts",params={"author_id":alice}).json()
        self.assertEqual([p["title"] for p in result],["Alice route"])
        self.assertEqual(result[0]["author_username"],"alice")
        for params in [{"offset":-1},{"limit":0},{"limit":101},{"category":"unknown"}]:
            self.assertEqual(self.client.get("/posts",params=params).status_code,422)

    def test_anonymous_upload_is_rejected(self):
        self.assertEqual(self.client.post("/uploads",files={"file":("photo.png",b"image","image/png")}).status_code,401)


if __name__ == "__main__":
    unittest.main()
