"""Verify own-profile publications with mocked API; no database writes."""
import json, threading
from functools import partial
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright, expect
from verify_main_contract import SPA

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SPA, directory='dist'))
threading.Thread(target=server.serve_forever, daemon=True).start()
user = dict(id=42, username='rider', avatar_url=None, email='rider@example.com', city=None, discipline=None, interests=[], bio=None, created_at='2026-11-01T10:00:00Z')
def post(id):
    return dict(id=id, title=f'Ride {id}', text='Cycling story', category='route', author=user, created_at='2026-11-05T10:00:00Z', photo_url=None, photos=[dict(id=i,url=f'/media/test-{i}.svg') for i in range(4)], like_count=0, liked_by_me=False)
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge', headless=True)
        for width in (1440, 390):
            context=browser.new_context(viewport=dict(width=width,height=950))
            state=dict(mode='posts', failed=False, requests=[])
            def api(route):
                url=urlparse(route.request.url)
                path=url.path.removeprefix('/api')
                if path=='/auth/me': return route.fulfill(json=user)
                if path=='/users/me/bikes': return route.fulfill(json=[dict(id=i,brand='Trek',model=f'Marlin {i}',year=2024,photo_url=None) for i in range(4)])
                if path=='/users/42/posts':
                    cursor=parse_qs(url.query).get('cursor',[None])[0]
                    state['requests'].append(cursor)
                    if state['mode']=='empty': return route.fulfill(json=dict(items=[],next_cursor=None))
                    if cursor and not state['failed']:
                        state['failed']=True
                        return route.fulfill(status=503,json=dict(detail='Try again'))
                    return route.fulfill(json=dict(items=[post(1),post(2)] if cursor else [post(1)],next_cursor=None if cursor else 'page2'))
                return route.fulfill(json={})
            context.route('**/api/**',api)
            context.route('**/media/test-*.svg', lambda route: route.fulfill(content_type='image/svg+xml',body='<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400"><rect width="640" height="400" fill="#dfe9d2"/><path d="M0 400L220 80L450 400M250 400L440 120L640 400" fill="#88a47b"/></svg>'))
            page=context.new_page()
            page.goto('http://localhost:5173/profile')
            expect(page.get_by_role('link',name='Публичный профиль и публикации',exact=False)).to_have_count(0)
            section=page.locator('.profile-publications')
            expect(section.get_by_role('heading',name='Ride 1',exact=True)).to_be_visible()
            expect(section.locator('.compact-post-gallery>button')).to_have_count(2)
            expect(section.locator('.gallery-more')).to_have_text('+2')
            section.get_by_role('button',name='Открыть фото 2 из 4').click()
            modal=page.get_by_role('dialog',name='Просмотр фотографий')
            expect(modal).to_be_visible()
            modal.get_by_role('button',name='Далее →').click()
            expect(modal.locator('.form-actions span')).to_have_text('3 / 4')
            modal.get_by_role('button',name='Закрыть',exact=True).click()
            expect(page.locator('.profile-cover')).to_have_count(0)
            aside=page.locator('.profile-aside')
            if width>1150:
                expect(aside).to_be_visible()
                expect(aside.locator('.profile-checklist li')).to_have_count(4)
                expect(aside.get_by_role('link',name='Заполнить профиль',exact=True)).to_have_attribute('href','/profile/edit')
                expect(aside.get_by_role('link',name='Найти людей',exact=True)).to_have_attribute('href','/people')
                expect(aside.get_by_role('link',name='Открыть публичный профиль',exact=False)).to_have_count(0)
            else:
                expect(aside).not_to_be_visible()
            expect(page.locator('.profile-bike-card')).to_have_count(4)
            page.locator('.profile-bike-photo summary').first.click()
            expect(page.locator('.profile-bike-photo[open]')).to_be_visible()
            page.locator('.profile-bike-photo summary').first.click()
            from pathlib import Path
            Path('output/profile-design').mkdir(parents=True,exist_ok=True)
            page.evaluate('scrollTo(0,0)')
            page.screenshot(path=f'output/profile-design/simple-profile-{width}.png',full_page=True)
            section.get_by_role('button',name='Загрузить ещё публикации').click()
            expect(section.get_by_role('alert')).to_contain_text('Try again')
            section.get_by_role('button',name='Повторить').click()
            expect(section.locator('.post-card')).to_have_count(2)
            expect(section.get_by_role('heading',name='Ride 2',exact=True)).to_be_visible()
            assert state['requests']==[None,'page2','page2'],state
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            logout=page.locator('.profile-hero .profile-logout button')
            expect(logout).to_be_visible()
            edit=page.locator('.profile-edit').bounding_box()
            signout=logout.bounding_box()
            assert signout['y'] > edit['y'] + edit['height']
            main_x=page.locator('.velo-main').bounding_box()['x']
            sidebar_x=page.locator('.velo-sidebar').bounding_box()['x']
            page.goto('http://localhost:5173/bikes')
            expect(page.locator('.velo-main')).to_be_visible()
            assert abs(page.locator('.velo-main').bounding_box()['x']-main_x)<1
            assert abs(page.locator('.velo-sidebar').bounding_box()['x']-sidebar_x)<1
            page.goto('http://localhost:5173/profile')
            state['mode']='empty'
            page.reload()
            expect(section.get_by_role('link',name='Создать первый пост')).to_be_visible()
            context.close()
            print(f'PASS {width}px: own posts, removed duplicate link, pagination, retry, deduplication and empty state')
        browser.close()
finally:
    server.shutdown()




