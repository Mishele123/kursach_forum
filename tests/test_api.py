import os
import sys
from pathlib import Path
import secrets
import unittest
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from main import create_app


class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        if not os.environ.get('POSTGRES_DB', '').startswith('forum_test_'):
            self.skipTest('Use python tests/run.py: a disposable test database is required')
        self.app = create_app()
        self.lifespan = self.app.router.lifespan_context(self.app)
        await self.lifespan.__aenter__()
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url='http://test')

    async def asyncTearDown(self):
        await self.client.aclose()
        await self.lifespan.__aexit__(None, None, None)

    async def account(self):
        username = 'user_' + secrets.token_hex(5)
        dto = {'username': username, 'email': username + '@example.com', 'password': 'GoodPassword123'}
        self.assertEqual((await self.client.post('/auth/register', json=dto)).status_code, 201)
        self.assertEqual((await self.client.post('/auth/login', json={k: dto[k] for k in ('email', 'password')})).status_code, 200)
        return dto

    async def test_posts_and_feed(self):
        post = {'title': 'Первый маршрут', 'text': 'Поездка к озеру', 'category': 'route'}
        self.assertEqual((await self.client.post('/posts', json=post)).status_code, 401)
        await self.account()
        ids = []
        for _ in range(3):
            response = await self.client.post('/posts', json=post)
            self.assertEqual(response.status_code, 201, response.text)
            ids.append(response.json()['id'])
        self.assertEqual((await self.client.post('/posts', json={**post, 'title': ' '})).status_code, 422)
        self.assertEqual((await self.client.post('/posts', json={**post, 'author_id': 42})).status_code, 422)
        self.client.cookies.clear()
        page = (await self.client.get('/posts', params={'limit': 2})).json()
        self.assertEqual([p['id'] for p in page['items']], ids[::-1][:2])
        following = (await self.client.get('/posts', params={'limit': 2, 'cursor': page['next_cursor']})).json()
        self.assertEqual(following['items'][0]['id'], ids[0])
        self.assertEqual((await self.client.get('/posts', params={'cursor': 'bad'})).status_code, 422)
        self.assertEqual((await self.client.get('/posts', params={'limit': 0})).status_code, 422)
        self.assertEqual((await self.client.get(f'/posts/{ids[0]}')).status_code, 200)
        self.assertEqual((await self.client.get('/posts/2147483647')).status_code, 404)

    async def test_photo_upload(self):
        from io import BytesIO
        from PIL import Image
        await self.account()
        post = (await self.client.post('/posts', json={'title': 'Фото', 'text': 'Велосипед', 'category': 'upgrade'})).json()
        url = f"/posts/{post['id']}/photo"
        self.assertIsNone(post['photo_url'])
        self.assertEqual((await self.client.put(url, files={'file': ('bad.jpg', b'not an image', 'image/jpeg')})).status_code, 415)
        self.assertEqual((await self.client.put(url, files={'file': ('big.jpg', b'x' * (5 * 1024 * 1024 + 1))})).status_code, 413)
        image = BytesIO(); Image.new('RGB', (8, 8), 'red').save(image, 'PNG')
        response = await self.client.put(url, files={'file': ('photo.png', image.getvalue(), 'image/png')})
        self.assertEqual(response.status_code, 200, response.text)
        first = response.json()['photo_url']
        self.assertEqual((await self.client.get(first)).status_code, 200)
        second = await self.client.put(url, files={'file': ('photo.png', image.getvalue(), 'image/png')})
        self.assertNotEqual(first, second.json()['photo_url'])
        self.assertEqual((await self.client.get(first)).status_code, 404)
        await self.account()
        self.assertEqual((await self.client.put(url, files={'file': ('photo.png', image.getvalue())})).status_code, 403)

    async def test_email_profile_logout(self):
        dto = await self.account()
        self.assertEqual((await self.client.post('/auth/register', json={**dto, 'username': 'other_name'})).status_code, 409)
        self.assertEqual((await self.client.post('/auth/register', json={**dto, 'email': 'bad'})).status_code, 422)
        self.assertEqual((await self.client.post('/auth/login', json={'email': dto['email'], 'password': 'WrongPassword'})).status_code, 401)
        self.assertEqual((await self.client.post('/auth/login', json={'email': dto['email'].upper(), 'password': dto['password']})).status_code, 200)
        cookie = self.client.cookies.get('session_id')
        self.assertTrue(cookie)
        profile = {'city': 'Самара', 'discipline': 'MTB', 'interests': ['маршруты', 'ремонт']}
        response = await self.client.patch('/users/me', json=profile)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['city'], 'Самара')
        self.assertNotIn('password_hash', response.json())
        await self.client.patch('/users/me', json={'bio': 'Люблю велосипеды'})
        self.assertEqual((await self.client.get('/auth/me')).json()['city'], 'Самара')
        self.assertEqual((await self.client.patch('/users/me', json={'role': 'admin'})).status_code, 422)
        await self.account()
        self.assertIsNone((await self.client.get('/users/me')).json()['city'])
        cookie = self.client.cookies.get('session_id')
        self.assertEqual((await self.client.post('/auth/logout')).status_code, 204)
        self.assertEqual((await self.client.get('/auth/me')).status_code, 401)
        self.client.cookies.set('session_id', cookie)
        self.assertEqual((await self.client.get('/auth/me')).status_code, 401)

    async def test_bikes_owned_by_current_user(self):
        bike = {'brand': 'Trek', 'model': 'Marlin', 'year': 2024}
        self.assertEqual((await self.client.post('/users/me/bikes', json=bike)).status_code, 401)
        await self.account()
        response = await self.client.post('/users/me/bikes', json=bike)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual((await self.client.get('/users/me/bikes')).json(), [response.json()])
        self.assertEqual((await self.client.post('/users/me/bikes', json={**bike, 'year': 2199})).status_code, 422)
        self.assertEqual((await self.client.post('/users/me/bikes', json={**bike, 'owner_id': 1})).status_code, 422)
        await self.account()
        self.assertEqual((await self.client.get('/users/me/bikes')).json(), [])

    async def test_deleted_banned_and_expired_sessions(self):
        from datetime import datetime, timezone, timedelta
        from config import Config
        from shared import new_session_maker
        from auth.models import UserModel
        from auth.infra import new_redis_client
        from sqlalchemy import select
        dto = await self.account()
        config = Config()
        maker = new_session_maker(config.postgres)
        try:
            async with maker() as db:
                user = await db.scalar(select(UserModel).where(UserModel.email == dto['email']))
                user.banned_until = datetime.now(timezone.utc) + timedelta(days=1)
                await db.commit()
            self.assertEqual((await self.client.get('/auth/me')).status_code, 403)
            async with maker() as db:
                user = await db.scalar(select(UserModel).where(UserModel.email == dto['email']))
                user.banned_until = None
                user.deleted_at = datetime.now(timezone.utc)
                await db.commit()
            self.assertEqual((await self.client.get('/auth/me')).status_code, 401)
            await self.account()
            client = new_redis_client(config.redis)
            try:
                await client.delete(f'{config.redis.key_prefix}:session:{self.client.cookies.get("session_id")}')
                self.assertEqual((await self.client.get('/auth/me')).status_code, 401)
            finally:
                await client.aclose()
        finally:
            await maker.kw['bind'].dispose()
