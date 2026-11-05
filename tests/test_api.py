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

    async def test_browser_origins_and_invalid_identifiers(self):
        preflight = await self.client.options('/posts', headers={
            'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'})
        self.assertEqual(preflight.status_code, 200)
        self.assertEqual(preflight.headers['access-control-allow-origin'], 'http://localhost:5173')
        self.assertEqual(preflight.headers['access-control-allow-credentials'], 'true')
        response = await self.client.post('/auth/logout', headers={'Origin': 'https://untrusted.example'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual((await self.client.get('/posts/999999999999999999999')).status_code, 422)
        self.assertEqual((await self.client.get('/posts/-1')).status_code, 422)

    async def test_registration_race_and_cookie(self):
        import asyncio
        username = 'race_' + secrets.token_hex(5)
        payload = {'username': username, 'email': username + '@example.com', 'password': 'GoodPassword123'}
        results = await asyncio.gather(*[self.client.post('/auth/register', json=payload) for _ in range(2)])
        self.assertEqual(sorted(r.status_code for r in results), [201, 409])
        response = await self.client.post('/auth/login', json={'email': payload['email'], 'password': payload['password'], 'remember_me': True})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('session_id', response.json())
        cookie = response.headers['set-cookie']
        self.assertIn('HttpOnly', cookie)
        self.assertIn('Max-Age=', cookie)
        self.assertIn('SameSite=lax', cookie)

    async def test_people_search_combined_filters(self):
        city = 'Город_' + secrets.token_hex(5)
        ids = []
        # First user has the desired brand and model on DIFFERENT bikes.
        for bikes in [[('Trek', 'Domane'), ('Giant', 'Marlin')],
                      [('Trek', 'Marlin'), ('Trek', 'Marlin 7')],
                      [('TREK', 'MARLIN')]]:
            await self.account()
            user = (await self.client.patch('/users/me', json={
                'city': city, 'discipline': 'MTB', 'interests': ['поездки']})).json()
            ids.append(user['id'])
            for brand, model in bikes:
                self.assertEqual((await self.client.post('/users/me/bikes', json={
                    'brand': brand, 'model': model, 'year': 2024})).status_code, 201)
        self.client.cookies.clear()
        filters = {'city': city.lower(), 'discipline': 'mtb', 'brand': 'trek', 'model': 'marlin', 'limit': 1}
        response = await self.client.get('/users', params=filters)
        self.assertEqual(response.status_code, 200, response.text)
        first = response.json()
        self.assertEqual([u['id'] for u in first['items']], [ids[1]])
        self.assertEqual(set(first['items'][0]), {'id', 'username', 'avatar_url', 'city', 'discipline', 'interests'})
        second = (await self.client.get('/users', params={**filters, 'cursor': first['next_cursor']})).json()
        self.assertEqual([u['id'] for u in second['items']], [ids[2]])
        self.assertIsNone(second['next_cursor'])
        for extra in [{'city': 'no_such_city'}, {'discipline': 'BMX'}, {'brand': '%'}, {'model': '_'}]:
            self.assertEqual((await self.client.get('/users', params={**filters, **extra})).json()['items'], [])
        self.assertEqual(len((await self.client.get('/users', params={'city': city})).json()['items']), 3)
        self.assertEqual((await self.client.get('/users', params={'cursor': 'bad'})).status_code, 422)
        self.assertEqual((await self.client.get('/users', params={'limit': 0})).status_code, 422)

    async def test_public_profile_posts_and_deleted_user(self):
        from datetime import datetime, timezone
        from config import Config
        from shared import new_session_maker
        from auth.models import UserModel
        dto = await self.account()
        user = (await self.client.get('/users/me')).json()
        uid = user['id']
        await self.client.post('/users/me/bikes', json={'brand': 'Trek', 'model': 'Marlin', 'year': 2024})
        ids = []
        for i in range(3):
            r = await self.client.post('/posts', json={'title': f'Пост {i}', 'text': 'Текст', 'category': 'route'})
            ids.append(r.json()['id'])
        await self.account()
        await self.client.post('/posts', json={'title': 'Чужой', 'text': 'Текст', 'category': 'route'})
        self.client.cookies.clear()
        r = await self.client.get(f'/users/{uid}')
        self.assertEqual(r.status_code, 200, r.text)
        profile = r.json()
        self.assertEqual(set(profile), {'id', 'username', 'avatar_url', 'city', 'discipline', 'interests', 'bikes'})
        self.assertEqual(len(profile['bikes']), 1)
        self.assertEqual(set(profile['bikes'][0]), {'id', 'brand', 'model', 'year', 'photo_url'})
        page = (await self.client.get(f'/users/{uid}/posts', params={'limit': 2})).json()
        self.assertEqual([p['id'] for p in page['items']], ids[::-1][:2])
        following = (await self.client.get(f'/users/{uid}/posts', params={'limit': 2, 'cursor': page['next_cursor']})).json()
        self.assertEqual([p['id'] for p in following['items']], [ids[0]])
        self.assertIsNone(following['next_cursor'])
        self.assertTrue(all(set(p['author']) == {'id', 'username', 'avatar_url'} for p in page['items']))
        self.assertEqual((await self.client.get('/users/me')).status_code, 401)
        self.assertEqual((await self.client.get('/users/me/bikes')).status_code, 401)
        self.assertEqual((await self.client.get('/users/2147483647')).status_code, 404)
        self.assertEqual((await self.client.get('/users/2147483647/posts')).status_code, 404)
        maker = new_session_maker(Config().postgres)
        try:
            async with maker() as db:
                record = await db.get(UserModel, uid)
                record.deleted_at = datetime.now(timezone.utc)
                await db.commit()
            self.assertEqual((await self.client.get(f'/users/{uid}')).status_code, 404)
            self.assertEqual((await self.client.get(f'/users/{uid}/posts')).status_code, 404)
            found = (await self.client.get('/users', params={'cursor': uid - 1, 'limit': 100})).json()
            self.assertNotIn(uid, [u['id'] for u in found['items']])
        finally:
            await maker.kw['bind'].dispose()

    async def test_post_search_across_pages_and_combined_filters(self):
        await self.account()
        term = 'Озеро' + secrets.token_hex(5)
        expected = []
        for title, text, category in [
            (term, 'Первый маршрут', 'route'),
            ('Второй маршрут', term.upper(), 'route'),
            (term.lower(), 'Третий маршрут', 'route'),
            (term, 'Обслуживание', 'maintenance'),
        ]:
            r = await self.client.post('/posts', json={'title': title, 'text': text, 'category': category})
            self.assertEqual(r.status_code, 201, r.text)
            if category == 'route': expected.append(r.json()['id'])
        # Matching posts are older than an entire default-sized first page.
        for i in range(21):
            r = await self.client.post('/posts', json={'title': f'Новый {i}', 'text': 'Без совпадения', 'category': 'route'})
            self.assertEqual(r.status_code, 201)
        self.client.cookies.clear()
        first = (await self.client.get('/posts')).json()
        self.assertTrue(set(expected).isdisjoint(p['id'] for p in first['items']))
        params = {'q': '  ' + term.swapcase() + '  ', 'category': 'route', 'limit': 2}
        seen = []
        for _ in range(10):
            response = await self.client.get('/posts', params=params)
            self.assertEqual(response.status_code, 200, response.text)
            page = response.json()
            seen.extend(p['id'] for p in page['items'])
            if page['next_cursor'] is None: break
            params['cursor'] = page['next_cursor']
        else: self.fail('Pagination did not terminate')
        self.assertEqual(seen, expected[::-1])
        self.assertEqual(len(seen), len(set(seen)))
        all_matches = (await self.client.get('/posts', params={'q': term})).json()
        self.assertEqual(len(all_matches['items']), 4)
        for params in [{'q': term, 'category': 'tricks'}, {'q': 'missing' + term}]:
            self.assertEqual((await self.client.get('/posts', params=params)).json(), {'items': [], 'next_cursor': None})
        self.assertEqual((await self.client.get('/posts', params={'category': 'unknown'})).status_code, 422)
        self.assertEqual((await self.client.get('/posts', params={'q': 'x' * 201})).status_code, 422)
        blank = (await self.client.get('/posts', params={'q': '   '})).json()
        self.assertEqual(blank, first)
        only_category = (await self.client.get('/posts', params={'category': 'route'})).json()
        self.assertTrue(all(p['category'] == 'route' for p in only_category['items']))

    async def test_post_search_treats_wildcards_as_text(self):
        await self.account()
        marker = secrets.token_hex(5)
        literal = marker + '%_'
        for text in [literal, marker + 'XX']:
            r = await self.client.post('/posts', json={'title': 'Поиск', 'text': text, 'category': 'upgrade'})
            self.assertEqual(r.status_code, 201)
        self.client.cookies.clear()
        result = (await self.client.get('/posts', params={'q': literal})).json()
        self.assertEqual([p['text'] for p in result['items']], [literal])

    async def test_comments_create_read_and_pagination(self):
        await self.account()
        post = (await self.client.post('/posts', json={'title':'Обсуждение','text':'Текст','category':'route'})).json()
        url = f"/posts/{post['id']}/comments"
        self.assertEqual((await self.client.get(url)).json(), {'items': [], 'next_cursor': None})
        self.client.cookies.clear()
        self.assertEqual((await self.client.post(url, json={'text':'Гость'})).status_code, 401)
        dto = await self.account()
        ids = []
        for i in range(3):
            r = await self.client.post(url, json={'text':f'  Ответ {i}  '})
            self.assertEqual(r.status_code, 201, r.text)
            self.assertEqual(r.json()['text'], f'Ответ {i}')
            self.assertEqual(r.json()['author']['username'], dto['username'])
            self.assertEqual(set(r.json()['author']), {'id','username','avatar_url'})
            ids.append(r.json()['id'])
        for payload in [{'text':'  \n '}, {'text':'x'*3001}, {'text':'Текст','author_id':1}]:
            self.assertEqual((await self.client.post(url, json=payload)).status_code, 422)
        self.assertEqual((await self.client.post('/posts/2147483647/comments', json={'text':'Текст'})).status_code, 404)
        self.assertEqual((await self.client.get('/posts/2147483647/comments')).status_code, 404)
        other = (await self.client.post('/posts', json={'title':'Другой','text':'Текст','category':'route'})).json()
        await self.client.post(f"/posts/{other['id']}/comments", json={'text':'В другой ветке'})
        self.client.cookies.clear()
        first = (await self.client.get(url, params={'limit':2})).json()
        self.assertEqual([c['id'] for c in first['items']], ids[::-1][:2])
        second = (await self.client.get(url, params={'limit':2,'cursor':first['next_cursor']})).json()
        self.assertEqual([c['id'] for c in second['items']], [ids[0]])
        self.assertIsNone(second['next_cursor'])
        self.assertEqual(len((await self.client.get(url)).json()['items']), 3)
        self.assertEqual((await self.client.get(url, params={'cursor':'bad'})).status_code, 422)

    async def test_likes_idempotency_and_viewer_state(self):
        owner = await self.account()
        owner_id = (await self.client.get('/auth/me')).json()['id']
        post = (await self.client.post('/posts', json={'title':'Лайки','text':'Текст','category':'route'})).json()
        pid = post['id']; url = f'/posts/{pid}/like'
        self.assertEqual((post['like_count'], post['liked_by_me']), (0, False))
        for _ in range(2):
            r = await self.client.put(url)
            self.assertEqual(r.status_code, 200, r.text)
            self.assertEqual(r.json(), {'post_id':pid,'like_count':1,'liked_by_me':True})
        for endpoint in [f'/posts/{pid}', '/posts', f'/users/{owner_id}/posts']:
            r = await self.client.get(endpoint)
            body = r.json()
            item = next(p for p in body['items'] if p['id']==pid) if 'items' in body else body
            self.assertEqual((item['like_count'],item['liked_by_me']), (1,True))
            self.assertEqual(r.headers['cache-control'], 'private, no-store')
        self.client.cookies.clear()
        guest = (await self.client.get(f'/posts/{pid}')).json()
        self.assertEqual((guest['like_count'],guest['liked_by_me']), (1,False))
        self.assertEqual((await self.client.put(url)).status_code, 401)
        self.assertEqual((await self.client.delete(url)).status_code, 401)
        self.client.cookies.set('session_id','expired-session')
        self.assertEqual((await self.client.get(f'/posts/{pid}')).status_code, 200)
        self.client.cookies.clear()
        await self.account()
        self.assertEqual((await self.client.put(url)).json()['like_count'], 2)
        for _ in range(2):
            self.assertEqual((await self.client.delete(url)).json(), {'post_id':pid,'like_count':1,'liked_by_me':False})
        self.assertEqual((await self.client.put('/posts/2147483647/like')).status_code, 404)
        self.assertEqual((await self.client.delete('/posts/2147483647/like')).status_code, 404)
        await self.client.post('/auth/logout')
        await self.client.post('/auth/login', json={k:owner[k] for k in ('email','password')})
        self.assertTrue((await self.client.get(f'/posts/{pid}')).json()['liked_by_me'])
        self.assertEqual((await self.client.delete(url)).json()['like_count'], 0)

    async def test_concurrent_likes_and_browser_delete(self):
        import asyncio
        await self.account()
        post = (await self.client.post('/posts', json={'title':'Одновременно','text':'Текст','category':'route'})).json()
        url = f"/posts/{post['id']}/like"
        results = await asyncio.gather(*[self.client.put(url) for _ in range(6)])
        self.assertTrue(all(r.status_code==200 and r.json()['like_count']==1 for r in results))
        results = await asyncio.gather(*[self.client.delete(url) for _ in range(6)])
        self.assertTrue(all(r.status_code==200 and r.json()['like_count']==0 for r in results))
        mixed = await asyncio.gather(self.client.put(url), self.client.delete(url))
        self.assertTrue(all(r.status_code==200 for r in mixed))
        current = (await self.client.get(f"/posts/{post['id']}")).json()
        self.assertEqual(current['like_count'], int(current['liked_by_me']))
        await self.client.delete(url)
        preflight = await self.client.options(url, headers={'Origin':'http://localhost:5173','Access-Control-Request-Method':'DELETE'})
        self.assertEqual(preflight.status_code, 200)
        self.assertIn('DELETE', preflight.headers['access-control-allow-methods'])
        self.assertEqual((await self.client.delete(url,headers={'Origin':'https://untrusted.example'})).status_code,403)

    async def test_likes_multiple_users_and_disabled_accounts(self):
        import asyncio
        from datetime import datetime, timezone, timedelta
        from config import Config
        from shared import new_session_maker
        from auth.models import UserModel
        await self.account()
        post = (await self.client.post('/posts', json={'title':'Поддержка','text':'Текст','category':'route'})).json()
        url = f"/posts/{post['id']}/like"
        first_id = (await self.client.get('/auth/me')).json()['id']
        first_cookie = {'Cookie':'session_id=' + self.client.cookies.get('session_id')}
        await self.account()
        second_id = (await self.client.get('/auth/me')).json()['id']
        second_cookie = {'Cookie':'session_id=' + self.client.cookies.get('session_id')}
        results = await asyncio.gather(*[self.client.put(url,headers=cookie)
                                        for cookie in [first_cookie,second_cookie]*3])
        self.assertTrue(all(r.status_code==200 for r in results))
        self.assertEqual((await self.client.get(f"/posts/{post['id']}")).json()['like_count'],2)
        maker = new_session_maker(Config().postgres)
        try:
            async with maker() as db:
                user = await db.get(UserModel, second_id)
                user.banned_until = datetime.now(timezone.utc) + timedelta(days=1)
                await db.commit()
            for method in [self.client.put,self.client.delete]:
                self.assertEqual((await method(url,headers=second_cookie)).status_code,403)
            async with maker() as db:
                user = await db.get(UserModel, second_id)
                user.deleted_at = datetime.now(timezone.utc)
                await db.commit()
            self.assertEqual((await self.client.put(url,headers=second_cookie)).status_code,401)
            data = (await self.client.get(f"/posts/{post['id']}",headers=first_cookie)).json()
            self.assertEqual((data['like_count'],data['liked_by_me']),(1,True))
            async with maker() as db:
                user = await db.get(UserModel, first_id)
                user.deleted_at = datetime.now(timezone.utc)
                await db.commit()
            await self.account()
            self.assertEqual((await self.client.put(url)).status_code,404)
            self.assertEqual((await self.client.delete(url)).status_code,404)
        finally:
            await maker.kw['bind'].dispose()

    async def test_bike_photos_and_avatars(self):
        from io import BytesIO
        from PIL import Image
        image = BytesIO()
        Image.new('RGB', (8, 8), 'blue').save(image, 'PNG')
        files = {'file': ('../../photo.png', image.getvalue(), 'image/png')}
        self.assertEqual((await self.client.put('/users/me/avatar', files=files)).status_code, 401)
        await self.account()
        user = (await self.client.get('/users/me')).json()
        bike = (await self.client.post('/users/me/bikes', json={'brand':'Trek','model':'Marlin','year':2024})).json()
        self.assertIsNone(bike['photo_url'])
        bike_url = f"/users/me/bikes/{bike['id']}/photo"
        for endpoint, field in [(bike_url, 'photo_url'), ('/users/me/avatar', 'avatar_url')]:
            before = set(self.app.state.upload_dir.iterdir())
            self.assertEqual((await self.client.put(endpoint, files={'file':('bad.png', b'invalid')})).status_code, 415)
            self.assertEqual((await self.client.put(endpoint, files={'file':('big.png', b'x'*(5*1024*1024+1))})).status_code, 413)
            self.assertEqual(set(self.app.state.upload_dir.iterdir()), before)
            first = await self.client.put(endpoint, files=files)
            self.assertEqual(first.status_code, 200, first.text)
            url = first.json()[field]
            content = await self.client.get(url)
            self.assertEqual(content.status_code, 200)
            self.assertEqual(Image.open(BytesIO(content.content)).format, 'JPEG')
            second = await self.client.put(endpoint, files=files)
            self.assertEqual(second.status_code, 200, second.text)
            self.assertNotEqual(url, second.json()[field])
            self.assertEqual((await self.client.get(url)).status_code, 404)
        avatar = second.json()['avatar_url']
        self.assertEqual((await self.client.get('/auth/me')).json()['avatar_url'], avatar)
        post = (await self.client.post('/posts', json={'title':'Avatar','text':'Test','category':'route'})).json()
        self.assertEqual(post['author']['avatar_url'], avatar)
        comment = await self.client.post(f"/posts/{post['id']}/comments", json={'text':'Avatar test'})
        self.assertEqual(comment.json()['author']['avatar_url'], avatar)
        self.assertEqual((await self.client.put('/users/me/bikes/2147483647/photo', files=files)).status_code, 404)
        await self.account()
        self.assertEqual((await self.client.put(bike_url, files=files)).status_code, 403)
        self.assertIsNone((await self.client.get('/users/me')).json()['avatar_url'])
        self.client.cookies.clear()
        profile = (await self.client.get(f"/users/{user['id']}")).json()
        self.assertEqual(profile['avatar_url'], avatar)
        self.assertIsNotNone(profile['bikes'][0]['photo_url'])
        self.assertNotIn('email', profile)
        self.assertEqual((await self.client.get(f"/posts/{post['id']}" )).json()['author']['avatar_url'], avatar)
        self.assertEqual((await self.client.get(f"/posts/{post['id']}/comments")).json()['items'][0]['author']['avatar_url'], avatar)

    async def test_post_gallery_atomicity_and_compatibility(self):
        from io import BytesIO
        from PIL import Image
        image = BytesIO()
        Image.new('RGB', (8, 8), 'green').save(image, 'PNG')
        photo = ('files', ('photo.png', image.getvalue(), 'image/png'))
        data = {'title':'Gallery ' + secrets.token_hex(5), 'text':'Several photos', 'category':'route'}
        self.assertEqual((await self.client.post('/posts/with-photos', data=data, files=[photo])).status_code, 401)
        await self.account()
        user = (await self.client.get('/users/me')).json()
        before = set(self.app.state.upload_dir.iterdir())
        bad = ('files', ('bad.png', b'bad', 'image/png'))
        invalid = await self.client.post('/posts/with-photos', data=data, files=[photo, bad])
        self.assertEqual(invalid.status_code, 415, invalid.text)
        self.assertEqual(set(self.app.state.upload_dir.iterdir()), before)
        self.assertEqual((await self.client.get('/posts', params={'q':data['title']})).json()['items'], [])
        self.assertEqual((await self.client.post('/posts/with-photos', data={**data,'title':' '}, files=[photo])).status_code, 422)
        created = await self.client.post('/posts/with-photos', data=data, files=[photo, photo])
        self.assertEqual(created.status_code, 201, created.text)
        post = created.json()
        self.assertEqual(len(post['photos']), 2)
        self.assertEqual(post['photo_url'], post['photos'][0]['url'])
        endpoint = f"/posts/{post['id']}/photos"
        before = set(self.app.state.upload_dir.iterdir())
        self.assertEqual((await self.client.post(endpoint, files=[photo, bad])).status_code, 415)
        self.assertEqual(set(self.app.state.upload_dir.iterdir()), before)
        self.assertEqual((await self.client.get(f"/posts/{post['id']}" )).json()['photos'], post['photos'])
        self.assertEqual((await self.client.post(endpoint, files=[photo]*11)).status_code, 422)
        self.assertEqual((await self.client.post(endpoint)).status_code, 422)
        added = await self.client.post(endpoint, files=[photo]*8)
        self.assertEqual(added.status_code, 201, added.text)
        self.assertEqual(len(added.json()['photos']), 10)
        self.assertEqual((await self.client.post(endpoint, files=[photo])).status_code, 422)
        changed = await self.client.put(f"/posts/{post['id']}/photo", files={'file':photo[1]})
        self.assertEqual(changed.status_code, 200, changed.text)
        gallery = changed.json()['photos']
        self.assertEqual(gallery[1:], added.json()['photos'][1:])
        self.assertEqual(gallery[0]['id'], post['photos'][0]['id'])
        self.assertEqual((await self.client.get(post['photo_url'])).status_code, 404)
        for item in gallery:
            self.assertEqual((await self.client.get(item['url'])).status_code, 200)
        await self.account()
        self.assertEqual((await self.client.post(endpoint, files=[photo])).status_code, 403)
        self.client.cookies.clear()
        self.assertEqual((await self.client.post(endpoint, files=[photo])).status_code, 401)
        for path in ['/posts', f"/users/{user['id']}/posts"]:
            items = (await self.client.get(path)).json()['items']
            found = next(p for p in items if p['id'] == post['id'])
            self.assertEqual(found['photos'], gallery)

    async def test_concurrent_gallery_limit(self):
        import asyncio
        from io import BytesIO
        from PIL import Image
        image = BytesIO()
        Image.new('RGB', (8, 8), 'red').save(image, 'PNG')
        photo = ('files', ('photo.png', image.getvalue(), 'image/png'))
        await self.account()
        post = (await self.client.post('/posts', json={'title':'Race','text':'Gallery','category':'route'})).json()
        self.assertEqual(post['photos'], [])
        endpoint = f"/posts/{post['id']}/photos"
        before = set(self.app.state.upload_dir.iterdir())
        results = await asyncio.gather(*[self.client.post(endpoint, files=[photo]*6) for _ in range(2)])
        self.assertEqual(sorted(r.status_code for r in results), [201, 422])
        self.assertEqual(len((await self.client.get(f"/posts/{post['id']}" )).json()['photos']), 6)
        self.assertEqual(len(set(self.app.state.upload_dir.iterdir()) - before), 6)

    async def test_password_change(self):
        dto = {'current_password':'GoodPassword123', 'new_password':'ChangedPassword456'}
        self.assertEqual((await self.client.put('/auth/password', json=dto)).status_code, 401)
        owner = await self.account()
        user = (await self.client.get('/auth/me')).json()
        for payload, status in [({**dto,'current_password':'WrongPassword'},400),
                                ({**dto,'new_password':'short'},422),
                                ({**dto,'new_password':dto['current_password']},422),
                                ({**dto,'user_id':123},422)]:
            self.assertEqual((await self.client.put('/auth/password', json=payload)).status_code, status)
        response = await self.client.put('/auth/password', json=dto)
        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(response.content, b'')
        self.assertEqual((await self.client.get('/auth/me')).json()['id'], user['id'])
        await self.client.post('/auth/logout')
        self.assertEqual((await self.client.post('/auth/login', json={'email':owner['email'],'password':dto['current_password']})).status_code, 401)
        self.assertEqual((await self.client.post('/auth/login', json={'email':owner['email'],'password':dto['new_password']})).status_code, 200)
        self.assertNotIn('password_hash', (await self.client.get('/auth/me')).json())

    async def test_concurrent_password_change(self):
        import asyncio
        await self.account()
        responses = await asyncio.gather(*[self.client.put('/auth/password', json={
            'current_password':'GoodPassword123', 'new_password':f'ChangedPassword{i}'}) for i in range(2)])
        self.assertEqual(sorted(r.status_code for r in responses), [204, 400])

    async def test_username_change_validation_and_public_authors(self):
        endpoint = '/users/me/username'
        self.assertEqual((await self.client.patch(endpoint, json={'username':'new_name'})).status_code, 401)
        other = await self.account()
        owner = await self.account()
        user = (await self.client.get('/auth/me')).json()
        post = (await self.client.post('/posts', json={'title':'Rename','text':'Test','category':'route'})).json()
        await self.client.post(f"/posts/{post['id']}/comments", json={'text':'Original author'})
        for name in ['', 'ab', 'a'*51, 'bad-name', 'имя', 'bad name', None]:
            self.assertEqual((await self.client.patch(endpoint, json={'username':name})).status_code, 422)
        self.assertEqual((await self.client.patch(endpoint, json={'username':'new_name','user_id':123})).status_code, 422)
        self.assertEqual((await self.client.patch(endpoint, json={'username':other['username'].upper()})).status_code, 409)
        self.assertEqual((await self.client.get('/auth/me')).json()['username'], owner['username'])
        name = 'renamed_' + secrets.token_hex(5)
        renamed = await self.client.patch(endpoint, json={'username':'  '+name+'  '})
        self.assertEqual(renamed.status_code, 200, renamed.text)
        self.assertEqual(renamed.json()['username'], name)
        self.assertEqual(renamed.json()['id'], user['id'])
        self.assertEqual((await self.client.patch(endpoint, json={'username':name})).status_code, 200)
        self.assertEqual((await self.client.get('/auth/me')).json()['username'], name)
        self.assertEqual((await self.client.get(f"/users/{user['id']}" )).json()['username'], name)
        self.assertEqual((await self.client.get(f"/posts/{post['id']}" )).json()['author']['username'], name)
        self.assertEqual((await self.client.get(f"/posts/{post['id']}/comments")).json()['items'][0]['author']['username'], name)
        await self.client.post('/auth/logout')
        login = await self.client.post('/auth/login', json={'email':owner['email'],'password':owner['password']})
        self.assertEqual(login.status_code, 200, login.text)
        self.assertEqual(login.json()['username'], name)
        await self.client.post('/auth/login', json={'email':other['email'],'password':other['password']})
        self.assertEqual((await self.client.get('/auth/me')).json()['username'], other['username'])

    async def test_concurrent_username_conflict(self):
        import asyncio
        await self.account()
        first_cookie = self.client.cookies.get('session_id')
        await self.account()
        second_cookie = self.client.cookies.get('session_id')
        name = 'claimed_' + secrets.token_hex(5)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url='http://test') as first, \
                   httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url='http://test') as second:
            first.cookies.set('session_id', first_cookie)
            second.cookies.set('session_id', second_cookie)
            results = await asyncio.gather(first.patch('/users/me/username', json={'username':name}),
                                           second.patch('/users/me/username', json={'username':name.upper()}))
        self.assertEqual(sorted(r.status_code for r in results), [200, 409])
