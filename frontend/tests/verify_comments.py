"""Browser checks for the comments panel against mocked API responses.

After npm run build: .venv/bin/python frontend/tests/verify_comments.py
Uses an isolated headless Chrome profile; does not write to the project database.
"""
import json
import threading
from functools import partial
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer
from playwright.sync_api import expect, sync_playwright
from verify_main_contract import SPA


def check(browser, base, width):
    user = dict(id=1, username='rider', email='rider@example.com', city=None,
                discipline=None, interests=[], bio=None, created_at='2026-11-04T10:00:00Z')
    post = dict(id=1, title='Маршрут к озеру', text='Обсуждение маршрута', category='route',
                author=dict(id=1, username='rider'), photo_url=None, created_at=user['created_at'])
    comments = [dict(id=i, post_id=1, author=post['author'], text=f'Комментарий {i}',
                     created_at=user['created_at']) for i in range(12, 0, -1)]
    state = dict(auth=False, fail_load=True, fail_send=True)
    context = browser.new_context(viewport=dict(width=width, height=900))
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))

    def api(route):
        parsed = urlparse(route.request.url)
        if not parsed.netloc.endswith(':8000') and not parsed.path.startswith('/api/'):
            return route.continue_()
        path = parsed.path.removeprefix('/api')
        def reply(data, status=200):
            route.fulfill(status=status, content_type='application/json', body=json.dumps(data), headers={'Access-Control-Allow-Origin':base,'Access-Control-Allow-Credentials':'true','Access-Control-Allow-Headers':'content-type'})
        if route.request.method == 'OPTIONS':
            return reply({},204)
        if path == '/auth/me':
            return reply(user if state['auth'] else {'detail':'Требуется вход'}, 200 if state['auth'] else 401)
        if path == '/posts/1': return reply(post)
        if path == '/posts/1/comments':
            if route.request.method == 'POST':
                if state['fail_send']:
                    state['fail_send'] = False
                    return reply({'detail':'Тестовая ошибка отправки'}, 503)
                text = route.request.post_data_json['text']
                comment = dict(id=13, post_id=1, author=post['author'], text=text, created_at=user['created_at'])
                comments.insert(0, comment)
                return reply(comment, 201)
            if state['fail_load']:
                state['fail_load'] = False
                return reply({'detail':'Тестовая ошибка загрузки'}, 503)
            query = parse_qs(parsed.query)
            cursor = int(query.get('cursor', ['2147483647'])[0])
            rows = [c for c in comments if c['id'] < cursor]
            return reply(dict(items=rows[:10], next_cursor=rows[9]['id'] if len(rows)>10 else None))
        if path == '/posts': return reply(dict(items=[post], next_cursor=None))
        return reply({'detail':'Not found'}, 404)

    page.route('**/*', api)
    page.goto(base + '/post/1')
    panel = page.locator('.comments-panel')
    expect(panel.get_by_role('heading', name='Комментарии', exact=True)).to_be_visible()
    expect(panel.get_by_role('link', name='Войдите', exact=True)).to_be_visible()
    expect(panel.get_by_role('alert')).to_contain_text('Тестовая ошибка загрузки')
    panel.get_by_role('button', name='Повторить загрузку').click()
    expect(panel.locator('.comment-item')).to_have_count(10)
    panel.get_by_role('button', name='Загрузить ещё комментарии').click()
    expect(panel.locator('.comment-item')).to_have_count(12)
    state['auth'] = True
    page.reload()
    field = panel.get_by_label('Ваш комментарий')
    expect(field).to_be_visible()
    submit = panel.get_by_role('button', name='Отправить', exact=True)
    field.fill('   ')
    expect(submit).to_be_disabled()
    text = 'Отличный маршрут! <script>window.commentXss = true</script>'
    field.fill(text)
    submit.click()
    expect(panel.get_by_role('alert')).to_contain_text('Тестовая ошибка отправки')
    expect(field).to_have_value(text)
    submit.click()
    expect(panel.get_by_role('status')).to_contain_text('Комментарий опубликован')
    expect(field).to_have_value('')
    expect(panel.locator('.comment-item').first).to_contain_text(text)
    page.reload()
    expect(panel.locator('.comment-item').first).to_contain_text(text)
    assert page.evaluate('window.commentXss') is None
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
    page.screenshot(path=str(Path(__file__).parent / 'artifacts' / f'comments-{width}.png'), full_page=True)
    assert not errors, errors
    context.close()
    print(f'PASS {width}px: guest, pagination, errors/retry, submit, reload, escaped text')


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SPA, directory=str(Path(__file__).resolve().parents[1] / 'dist')))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='msedge', headless=True)
            for width in (1440, 390):
                check(browser, f'http://127.0.0.1:{server.server_port}', width)
            browser.close()
    finally:
        server.shutdown()
