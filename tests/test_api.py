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
        dto = {'username': username, 'password': 'GoodPassword123'}
        self.assertEqual((await self.client.post('/auth/register', json=dto)).status_code, 201)
        self.assertEqual((await self.client.post('/auth/login', json=dto)).status_code, 200)
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
