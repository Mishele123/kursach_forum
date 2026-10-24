"""Browser checks against mocked main API shapes; no backend or database writes.

Run after npm run build, from the repository root:
.venv/Scripts/python.exe frontend/tests/verify_main_contract.py
"""
import io
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from PIL import Image
from playwright.sync_api import expect, sync_playwright


class SPA(SimpleHTTPRequestHandler):
    def do_GET(self):
        if not Path(self.translate_path(self.path)).is_file():
            self.path = '/index.html'
        try:
            super().do_GET()
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            pass  # Navigation can cancel an in-flight asset response.

    def log_message(self, *_):
        pass


def check(browser, base, width):
    user = dict(id=1, username='rider', email='rider@example.com', city=None,
                discipline=None, interests=[], bio=None, created_at='2026-10-24T10:00:00Z')
    state = dict(auth=False, bikes=[], created=0, uploads=0, fail_photo=True)
    failures, errors = [], []
    posts = [dict(id=i, author=dict(id=1, username='rider'), title=f'Route {i}',
                  text='Plain <script> text', category='route', photo_url=None,
                  created_at='2026-10-24T10:00:00Z') for i in range(12, 0, -1)]

    def api(route):
        req = route.request
        url = urlparse(req.url)
        path = url.path.removeprefix('/api')
        if not url.netloc.endswith(':8000') and not url.path.startswith('/api/'):
            return route.continue_()
        data = req.post_data_json if req.method in ('POST', 'PATCH') else None
        status, result = 200, None
        try:
            if path == '/auth/register':
                assert set(data) == {'username', 'email', 'password'}
                status, result = 201, {'username': data['username']}
            elif path == '/auth/login':
                assert set(data) <= {'email', 'password', 'remember_me'}
                assert data['email'] == user['email']
                if data['password'] == 'wrongpass':
                    status, result = 401, {'detail': 'Неверный пароль'}
                else:
                    state['auth'] = True
                    result = {'username': user['username']}
            elif path == '/auth/me':
                status, result = (200, user) if state['auth'] else (401, {'detail': 'Unauthorized'})
            elif path == '/auth/logout':
                state['auth'] = False
                status = 204
            elif path == '/users/me' and req.method == 'PATCH':
                assert set(data) == {'city', 'discipline', 'interests', 'bio'}
                assert isinstance(data['interests'], list)
                user.update(data)
                result = user
            elif path == '/users/me/bikes':
                if req.method == 'POST':
                    assert set(data) == {'brand', 'model', 'year'}
                    state['bikes'].append(dict(id=1, **data))
                    status, result = 201, state['bikes'][-1]
                else:
                    result = state['bikes']
            elif path == '/posts' and req.method == 'GET':
                query = parse_qs(url.query)
                assert set(query) <= {'limit', 'cursor'}
                result = {'items': posts[10:] if 'cursor' in query else posts[:10],
                          'next_cursor': None if 'cursor' in query else 'next+cursor='}
                if 'cursor' in query:
                    assert query['cursor'] == ['next+cursor=']
            elif path == '/posts' and req.method == 'POST':
                assert set(data) == {'title', 'text', 'category'}
                assert data['category'] in ('route', 'maintenance', 'upgrade', 'tricks')
                state['created'] += 1
                result = dict(posts[0], **data, id=100+state['created'])
                posts.insert(0, result)
                status = 201
            elif path.endswith('/photo') and req.method == 'PUT':
                assert 'multipart/form-data; boundary=' in req.headers['content-type']
                state['uploads'] += 1
                if state['fail_photo']:
                    state['fail_photo'] = False
                    status, result = 415, {'detail': 'Повторите загрузку фото'}
                else:
                    result = next(p for p in posts if p['id'] == int(path.split('/')[2]))
                    result['photo_url'] = '/media/test.jpg'
            elif path.startswith('/posts/') and req.method == 'GET':
                result = next(p for p in posts if p['id'] == int(path.split('/')[2]))
            elif path == '/media/test.jpg':
                image = io.BytesIO()
                Image.new('RGB', (10, 10)).save(image, 'JPEG')
                return route.fulfill(status=200, content_type='image/jpeg', body=image.getvalue())
            else:
                raise AssertionError(f'Unexpected API request: {req.method} {path}')
        except Exception as error:
            failures.append(str(error))
            status, result = 500, {'detail': str(error)}
        route.fulfill(status=status, content_type='application/json',
                      body='' if status == 204 else json.dumps(result),
                      headers={'Access-Control-Allow-Origin': base,
                               'Access-Control-Allow-Credentials': 'true'})

    context = browser.new_context(viewport={'width': width, 'height': 900})
    context.route('**/*', api)
    page = context.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(base+'/feed')
    expect(page.locator('.post-card')).to_have_count(10)
    page.get_by_role('button', name='Загрузить ещё', exact=True).click()
    expect(page.locator('.post-card')).to_have_count(12)
    expect(page.get_by_role('button', name='Загрузить ещё', exact=True)).to_have_count(0)
    page.goto(base+'/profile/edit')
    page.wait_for_url('**/login')
    page.get_by_label('Email', exact=True).fill(user['email'])
    page.get_by_label('Пароль', exact=True).fill('wrongpass')
    page.get_by_role('button', name='Войти', exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('Неверный пароль')
    page.get_by_label('Пароль', exact=True).fill('secret123')
    page.get_by_label('Запомнить меня').check()
    page.get_by_role('button', name='Войти', exact=True).click()
    page.wait_for_url('**/feed')
    page.reload()
    page.goto(base+'/profile/edit')
    page.get_by_label('Город', exact=True).fill('Самара')
    page.get_by_label('Интересы (через запятую)').fill('MTB, маршруты')
    page.get_by_role('button', name='Сохранить изменения').click()
    page.wait_for_url('**/profile')
    expect(page.locator('.velo-main')).to_contain_text('MTB, маршруты')
    page.goto(base+'/bikes/add')
    for label, value in [('Бренд *', 'Trek'), ('Модель *', 'Marlin'), ('Год выпуска *', '2024')]:
        page.get_by_label(label, exact=True).fill(value)
    page.get_by_role('button', name='Добавить велосипед', exact=True).click()
    page.wait_for_url('**/bikes')
    expect(page.locator('.bike-grid')).to_contain_text('Trek Marlin')
    for with_photo in (False, True):
        page.goto(base+'/post/create')
        page.get_by_label('Заголовок *', exact=True).fill('New route')
        page.get_by_label('Текст публикации *', exact=True).fill('A plain text post')
        if with_photo:
            image = io.BytesIO()
            Image.new('RGB', (10, 10)).save(image, 'PNG')
            page.get_by_label('+ Добавьте одну фотографию').set_input_files(
                {'name':'ride.png', 'mimeType':'image/png', 'buffer':image.getvalue()})
        page.get_by_role('button', name='Опубликовать', exact=True).click()
        if with_photo:
            expect(page.get_by_role('alert')).to_be_visible()
            page.get_by_role('button', name='Повторить загрузку фото', exact=True).click()
        page.wait_for_url('**/post/*')
        expect(page.get_by_role('heading', name='New route', exact=True)).to_be_visible()
        if with_photo:
            expect(page.get_by_alt_text('New route')).to_be_visible()
    assert state['created'] == 2, 'Retry must not create a duplicate post'
    assert state['uploads'] == 2
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
    page.goto(base+'/profile')
    page.get_by_role('button', name='Выйти из аккаунта').click()
    page.wait_for_url('**/login')
    page.goto(base+'/register')
    page.get_by_label('Имя пользователя', exact=True).fill('invalid name')
    page.get_by_label('Email', exact=True).fill(user['email'])
    page.get_by_label('Пароль', exact=True).fill('secret123')
    page.get_by_label('Подтвердите пароль', exact=True).fill('secret123')
    assert not page.locator('input[name=username]').evaluate('(input) => input.checkValidity()')
    page.get_by_label('Имя пользователя', exact=True).fill('rider')
    page.get_by_role('button', name='Создать аккаунт', exact=True).click()
    page.wait_for_url('**/feed')
    assert not failures, failures
    assert not errors, errors
    context.close()
    print(f'PASS {width}px: cursor feed, auth error/login/reload/logout, profile, bikes, text/photo post and upload retry')


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SPA, directory=str(Path(__file__).resolve().parents[1]/'dist')))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='msedge', headless=True)
            for width in (1440, 390):
                check(browser, f'http://127.0.0.1:{server.server_port}', width)
            browser.close()
    finally:
        server.shutdown()
