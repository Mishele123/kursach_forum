"""Browser contract checks for Sprint 2, desktop and mobile. No backend writes.
Run after npm run build: .venv/Scripts/python.exe frontend/tests/verify_sprint2.py
"""
import io
import json
import re
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from PIL import Image
from playwright.sync_api import sync_playwright, expect
from verify_main_contract import SPA


def check(browser, base, width):
    user = dict(id=1, username='rider', avatar_url=None, email='rider@example.com', city='Самара',
                discipline='MTB', interests=['Маршруты'], bio=None, created_at='2026-11-01T10:00:00Z')
    bike = dict(id=1, brand='Trek', model='Marlin', year=2024, photo_url=None)
    def post(ident, title):
        return dict(id=ident, title=title, text='История маршрута', category='route',
                    author={k:user[k] for k in ('id', 'username', 'avatar_url')},
                    photos=[], photo_url=None, like_count=0, liked_by_me=False, created_at=user['created_at'])
    posts = [post(1, 'First ride'), post(2, 'Hidden lake')]
    state = dict(auth=True, fail_like=True, fail_people=True, fail_gallery=True, creates=0, comments=[],
                 searches=[], people_queries=[], password_calls=0)
    failures, errors = [], []
    image = io.BytesIO()
    Image.new('RGB', (12, 12), 'green').save(image, 'PNG')
    photo = dict(name='ride.png', mimeType='image/png', buffer=image.getvalue())

    def api(route):
        request = route.request
        url = urlparse(request.url)
        if not url.netloc.endswith(':8000') and not url.path.startswith('/api/') and not url.path.startswith('/media/'):
            return route.continue_()
        path = url.path.removeprefix('/api')
        if path.startswith('/media/'):
            return route.fulfill(status=200, content_type='image/png', body=image.getvalue())
        method = request.method
        cors = {'Access-Control-Allow-Origin':base,'Access-Control-Allow-Credentials':'true','Access-Control-Allow-Methods':'GET, POST, PUT, PATCH, DELETE, OPTIONS','Access-Control-Allow-Headers':'content-type'}
        if method == 'OPTIONS':
            return route.fulfill(status=204,headers=cors)
        data = request.post_data_json if method in ('PATCH', 'PUT', 'POST') and 'application/json' in request.headers.get('content-type', '') else None
        status, result = 200, None
        try:
            if path == '/auth/me':
                status, result = (200,user) if state['auth'] else (401,dict(detail='Unauthorized'))
            elif path == '/auth/logout':
                state['auth'] = False
                status = 204
            elif path == '/posts' and method == 'GET':
                query = parse_qs(url.query)
                state['searches'].append(query)
                if query.get('q') == ['missing']:
                    result = dict(items=[], next_cursor=None)
                elif 'q' in query:
                    assert query['q'] == ['lake']
                    assert query.get('category', ['route']) == ['route']
                    assert 'cursor' not in query
                    result = dict(items=[posts[1]], next_cursor=None)
                else:
                    result = dict(items=[posts[1]] if 'cursor' in query else [posts[0]], next_cursor=None if 'cursor' in query else 'next+cursor=')
            elif path == '/users':
                query = parse_qs(url.query)
                state['people_queries'].append(query)
                if state['fail_people']:
                    state['fail_people'] = False
                    status, result = 503, dict(detail='Поиск временно недоступен')
                else:
                    person = {k:user[k] for k in ('id','username','avatar_url','city','discipline','interests')}
                    if 'cursor' in query:
                        person = dict(person, id=2, username='other')
                    result = dict(items=[] if query.get('city') == ['missing'] else [person], next_cursor=None if 'cursor' in query else 1)
            elif path == '/users/1':
                result = {k:user[k] for k in ('id','username','avatar_url','city','discipline','interests')}
                result['bikes'] = [bike]
            elif path == '/users/1/posts':
                query = parse_qs(url.query)
                result = dict(items=[posts[1]] if 'cursor' in query else [posts[0]],next_cursor=None if 'cursor' in query else '1')
            elif path == '/users/me/bikes':
                result = [bike]
            elif path == '/users/me/bikes/1/photo':
                assert 'multipart/form-data' in request.headers['content-type']
                bike['photo_url'] = '/media/bike.jpg'
                result = bike
            elif path == '/users/me/avatar':
                user['avatar_url'] = '/media/avatar.jpg'
                result = user
            elif path == '/users/me/username':
                if data['username'] == 'taken':
                    status, result = 409, dict(detail='Имя пользователя уже занято')
                else:
                    user['username'] = data['username']
                    result = user
            elif path == '/users/me' and method == 'PATCH':
                user.update(data)
                result = user
            elif path == '/auth/password':
                state['password_calls'] += 1
                if data['current_password'] != 'GoodPassword123':
                    status, result = 400, dict(detail='Неверный текущий пароль')
                else:
                    assert data['new_password'] == 'ChangedPassword123'
                    status = 204
            elif path == '/posts/with-photos':
                assert 'multipart/form-data' in request.headers['content-type']
                assert request.post_data_buffer.count(b'name="files"') == 2
                if state['fail_gallery']:
                    state['fail_gallery'] = False
                    status, result = 415, dict(detail='Неверная фотография')
                else:
                    state['creates'] += 1
                    result = post(3, 'New gallery')
                    result.update(photos=[dict(id=1,url='/media/one.jpg'),dict(id=2,url='/media/two.jpg')],photo_url='/media/one.jpg')
                    posts.append(result)
                    status = 201
            elif path.endswith('/like'):
                if state['fail_like']:
                    state['fail_like'] = False
                    status, result = 503, dict(detail='Повторите попытку')
                else:
                    target = next(p for p in posts if p['id'] == int(path.split('/')[2]))
                    target.update(like_count=int(method=='PUT'),liked_by_me=method=='PUT')
                    result = dict(like_count=target['like_count'],liked_by_me=target['liked_by_me'])
            elif path.endswith('/photos'):
                target = posts[-1]
                target['photos'].append(dict(id=3,url='/media/three.jpg'))
                result = target
            elif path.endswith('/comments'):
                if method == 'POST':
                    state['comments'].insert(0,dict(id=1,post_id=int(path.split('/')[2]),text=data['text'],created_at=user['created_at'],author={k:user[k] for k in ('id','username','avatar_url')}))
                    status, result = 201, state['comments'][0]
                else:
                    result = dict(items=state['comments'],next_cursor=None)
            elif path.startswith('/posts/'):
                result = next(p for p in posts if p['id'] == int(path.split('/')[2]))
            else:
                raise AssertionError(f'Unexpected request: {method} {path}')
        except Exception as error:
            failures.append(str(error))
            status, result = 500, dict(detail=str(error))
        route.fulfill(status=status,content_type='application/json',body='' if status==204 else json.dumps(result),headers=cors)

    context = browser.new_context(viewport=dict(width=width,height=900))
    context.route('**/*',api)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(base+'/feed')
    expect(page.locator('.post-card')).to_have_count(1)
    page.get_by_role('button',name='Загрузить ещё',exact=True).click()
    expect(page.locator('.post-card')).to_have_count(2)
    page.get_by_label('Поиск публикаций',exact=True).fill('lake')
    page.get_by_role('button',name='Найти',exact=True).click()
    expect(page.locator('.post-card')).to_have_count(1)
    expect(page.locator('.post-card')).to_contain_text('Hidden lake')
    page.get_by_role('button',name='Маршруты',exact=True).click()
    expect(page.locator('.post-card')).to_have_count(1)
    assert parse_qs(urlparse(page.url).query) == dict(q=['lake'],category=['route'])
    like = page.get_by_role('button',name='♡ Нравится',exact=False)
    like.click()
    expect(page.get_by_role('alert')).to_contain_text('Повторите попытку')
    expect(like).to_have_attribute('aria-pressed','false')
    like.click()
    expect(page.get_by_role('button',name='♥ Нравится',exact=False)).to_have_attribute('aria-pressed','true')
    page.reload()
    page.get_by_role('button',name='♥ Нравится',exact=False).click()
    expect(page.get_by_role('button',name='♡ Нравится',exact=False)).to_have_attribute('aria-pressed','false')
    page.get_by_label('Поиск публикаций',exact=True).fill('missing')
    page.get_by_role('button',name='Найти',exact=True).click()
    expect(page.get_by_role('heading',name='Публикации не найдены')).to_be_visible()
    page.goto(base+'/people')
    expect(page.get_by_role('alert')).to_contain_text('Поиск временно недоступен')
    page.get_by_role('button',name='Повторить',exact=True).click()
    expect(page.locator('.person-card')).to_have_count(1)
    page.get_by_role('button',name='Загрузить ещё людей').click()
    expect(page.locator('.person-card')).to_have_count(2)
    for label,value in [('Город','Самара'),('Дисциплина','MTB'),('Бренд велосипеда','Trek'),('Модель велосипеда','Marlin')]:
        page.get_by_label(label,exact=True).fill(value)
    page.get_by_role('button',name='Найти людей').click()
    expect(page.locator('.person-card')).to_have_count(1)
    assert state['people_queries'][-1]['brand'] == ['Trek'] and 'cursor' not in state['people_queries'][-1]
    page.get_by_label('Город',exact=True).fill('missing')
    page.get_by_role('button',name='Найти людей').click()
    expect(page.get_by_role('heading',name='Пока никого не нашли')).to_be_visible()
    page.get_by_label('Город',exact=True).fill('Самара')
    page.get_by_role('button',name='Найти людей').click()
    expect(page.locator('.person-card')).to_have_count(1)
    page.locator('.person-card').click()
    expect(page.get_by_role('heading',name='rider',exact=True)).to_be_visible()
    page.get_by_role('button',name='Загрузить ещё публикации').click()
    expect(page.locator('.post-card')).to_have_count(2)
    page.goto(base+'/profile/edit')
    expect(page.get_by_role('heading',name='Фото профиля',exact=True)).to_be_visible()
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), 'Settings overflow'
    page.screenshot(path=str(Path(__file__).parent / 'artifacts' / f'settings-{width}.png'),full_page=True)
    page.get_by_label('Новое имя пользователя',exact=True).fill('taken')
    page.get_by_role('button',name='Изменить имя',exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('уже занято')
    page.get_by_label('Новое имя пользователя',exact=True).fill('renamed_rider')
    page.get_by_role('button',name='Изменить имя',exact=True).click()
    expect(page.get_by_role('status')).to_contain_text('Имя пользователя обновлено')
    page.get_by_label('Текущий пароль',exact=True).fill('WrongPassword')
    page.get_by_label('Новый пароль',exact=True).fill('ChangedPassword123')
    page.get_by_label('Повторите новый пароль',exact=True).fill('MismatchPassword')
    page.get_by_role('button',name='Изменить пароль',exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('не совпадают')
    assert state['password_calls'] == 0
    page.get_by_label('Повторите новый пароль',exact=True).fill('ChangedPassword123')
    page.get_by_role('button',name='Изменить пароль',exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('Неверный текущий пароль')
    page.get_by_label('Текущий пароль',exact=True).fill('GoodPassword123')
    page.get_by_role('button',name='Изменить пароль',exact=True).click()
    expect(page.get_by_text('Пароль изменён',exact=True)).to_be_visible()
    page.locator('.photo-upload input[type=file]').set_input_files(photo)
    page.get_by_role('button',name='Сохранить аватар',exact=True).click()
    expect(page.locator('.velo-header .avatar img')).to_have_attribute('src',re.compile(r'/media/avatar[.]jpg$'))
    page.goto(base+'/bikes')
    page.locator('input[type=file]').set_input_files(photo)
    page.get_by_role('button',name='Загрузить фото',exact=True).click()
    expect(page.locator('.bike-photo')).to_be_visible()
    page.goto(base+'/post/create')
    page.get_by_label('Заголовок *',exact=True).fill('New gallery')
    page.get_by_label('Текст публикации *',exact=True).fill('Gallery body')
    page.locator('input[type=file]').set_input_files(dict(name='invalid.txt',mimeType='text/plain',buffer=b'invalid'))
    expect(page.get_by_role('alert')).to_contain_text('Выберите JPEG или PNG')
    page.locator('input[type=file]').set_input_files([photo]*11)
    expect(page.get_by_role('alert')).to_contain_text('Не более 10 фото')
    page.locator('input[type=file]').set_input_files([photo,dict(photo,name='ride2.png')])
    expect(page.locator('.photo-previews img')).to_have_count(2)
    page.get_by_role('button',name='Опубликовать',exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('Неверная фотография')
    page.get_by_role('button',name='Опубликовать',exact=True).click()
    page.wait_for_url('**/post/3')
    expect(page.locator('.post-gallery img')).to_have_count(2)
    assert state['creates'] == 1
    page.get_by_role('button',name='Открыть фото 1 из 2',exact=True).click()
    expect(page.get_by_role('dialog')).to_be_visible()
    page.get_by_role('button',name='Далее →',exact=True).click()
    expect(page.get_by_role('dialog')).to_contain_text('2 / 2')
    page.keyboard.press('Escape')
    expect(page.get_by_role('dialog')).not_to_be_visible()
    page.locator('.photo-upload input[type=file]').set_input_files(photo)
    page.get_by_role('button',name='Загрузить фото',exact=True).click()
    expect(page.locator('.post-gallery img')).to_have_count(3)
    page.get_by_label('Ваш комментарий').fill('Отличный маршрут')
    page.get_by_role('button',name='Отправить',exact=True).click()
    expect(page.locator('.comment-item')).to_contain_text('Отличный маршрут')
    expect(page.locator('.comment-item .avatar img')).to_be_visible()
    page.reload()
    expect(page.locator('.comment-item')).to_contain_text('Отличный маршрут')
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), 'Horizontal overflow'
    page.screenshot(path=str(Path(__file__).parent / 'artifacts' / f'sprint2-{width}.png'),full_page=True)
    state['auth'] = False
    page.goto(base+'/post/3')
    expect(page.get_by_text('Войти, чтобы поставить лайк',exact=False)).to_be_visible()
    expect(page.locator('.comments-login')).to_be_visible()
    assert not failures, failures
    assert not errors, errors
    context.close()
    print(f'PASS {width}px: server search/reset, people/profile pagination, likes/errors, username/password, avatar/bike photos, gallery/retry, comments and guest states')


if __name__ == '__main__':
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SPA,directory=str(Path(__file__).resolve().parents[1]/'dist')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(channel='msedge',headless=True)
            for width in (1440,390):
                check(browser,f'http://127.0.0.1:{server.server_port}',width)
            browser.close()
    finally:
        server.shutdown()
