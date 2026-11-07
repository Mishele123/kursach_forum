"""Directory UI checks using mocked data, without database changes."""
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

def person(id):
    return dict(id=id,username=f'rider_{id}',avatar_url=None,city='Самара',discipline='Гравел',interests=['Путешествия','Город'])
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    for width in (1440,390):
        ctx=browser.new_context(viewport=dict(width=width,height=1000))
        state=dict(failed=False,requests=[])
        def api(route):
            url=urlparse(route.request.url);path=url.path.removeprefix('/api')
            if path=='/auth/me':return route.fulfill(status=401,json=dict(detail='Unauthorized'))
            if path=='/users':
                q=parse_qs(url.query);state['requests'].append(q)
                if 'cursor' in q and not state['failed']:
                    state['failed']=True
                    return route.fulfill(status=503,json=dict(detail='Try again'))
                if q.get('city')==['Nobody']:return route.fulfill(json=dict(items=[],next_cursor=None))
                return route.fulfill(json=dict(items=[person(1),person(2)] if 'cursor' not in q else [person(2),person(3)],next_cursor=None if 'cursor' in q else 2))
            return route.fulfill(json={})
        ctx.route('**/api/**',api)
        page=ctx.new_page();errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://localhost:5173/people')
        expect(page.locator('.people-person')).to_have_count(2)
        page.get_by_label('Город',exact=True).fill('Самара')
        page.get_by_label('Бренд',exact=True).fill('Trek')
        page.locator('.people-bike-filters summary').click()
        page.get_by_role('button',name='Найти людей',exact=True).click()
        expect(page).to_have_url('http://localhost:5173/people?city=%D0%A1%D0%B0%D0%BC%D0%B0%D1%80%D0%B0&brand=Trek')
        expect(page.locator('.people-person')).to_have_count(2)
        assert state['requests'][-1]['brand']==['Trek']
        page.get_by_role('button',name='Показать ещё').click()
        expect(page.get_by_role('alert')).to_contain_text('Try again')
        page.get_by_role('button',name='Повторить',exact=True).click()
        expect(page.locator('.people-person')).to_have_count(3)
        expect(page.locator('.people-person').first).to_have_attribute('href','/users/1')
        page.get_by_role('button',name='Сбросить',exact=True).click()
        expect(page.get_by_label('Город',exact=True)).to_have_value('')
        expect(page.get_by_label('Бренд',exact=True)).to_have_value('')
        expect(page.locator('.people-person')).to_have_count(2)
        page.get_by_label('Город',exact=True).fill('draft')
        page.get_by_role('button',name='Сбросить',exact=True).click()
        expect(page.get_by_label('Город',exact=True)).to_have_value('')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        Path('output/people-design').mkdir(parents=True,exist_ok=True)
        page.evaluate('scrollTo(0,0)');page.screenshot(path=f'output/people-design/people-{width}.png',full_page=True)
        page.get_by_label('Город',exact=True).fill('Nobody')
        page.get_by_role('button',name='Найти людей',exact=True).click()
        expect(page.get_by_role('heading',name='Пока никого не нашли')).to_be_visible()
        assert not errors,errors
        ctx.close()
        print(f'PASS {width}px: filters, collapsed fields, reset, pagination, retry, deduplication, links and empty state')
    browser.close()
