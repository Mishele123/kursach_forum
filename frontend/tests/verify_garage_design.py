"""Garage interactions using mocked API and uploads; no database writes."""
import io
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright, expect
png=io.BytesIO();Image.new('RGB',(640,360),(160,185,145)).save(png,'PNG');photo=png.getvalue()
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    for width in (1440,390):
        bikes=[dict(id=1,brand='Trek',model='Marlin 6',year=2022,photo_url=None),dict(id=2,brand='Canyon',model='Grizl 7',year=2024,photo_url='/media/bike.png')]
        state=dict(uploads=0,empty=False)
        context=browser.new_context(viewport=dict(width=width,height=1000))
        def api(route):
            path=route.request.url.split('/api')[-1].split('?')[0]
            if path=='/auth/me':return route.fulfill(json=dict(id=1,username='rider',avatar_url=None,city=None,discipline=None,interests=[],bio=None,email=None,created_at='2026-11-01T10:00:00Z'))
            if path=='/users/me/bikes':return route.fulfill(json=[] if state['empty'] else bikes)
            if path=='/users/me/bikes/1/photo':
                state['uploads']+=1
                if state['uploads']==1:return route.fulfill(status=503,json=dict(detail='Try again'))
                bikes[0]['photo_url']='/media/saved.png'
                return route.fulfill(json=bikes[0])
            return route.fulfill(json={})
        context.route('**/api/**',api)
        context.route('**/media/*.png',lambda route:route.fulfill(content_type='image/png',body=photo))
        page=context.new_page();errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://localhost:5173/bikes')
        cards=page.locator('.garage-bike-card');expect(cards).to_have_count(2)
        first=cards.first
        expect(first.locator('.bike-no-photo')).to_be_visible()
        expect(cards.nth(1).locator('img.bike-photo')).to_be_visible()
        expect(page.locator('.garage-photo-editor')).to_have_count(0)
        first.get_by_role('button',name='+ Добавить фото',exact=True).click()
        expect(first.get_by_role('button',name='Сохранить фото')).to_be_disabled()
        first.locator('input[type=file]').set_input_files(dict(name='bike.png',mimeType='image/png',buffer=photo))
        first.get_by_role('button',name='Отмена',exact=True).click()
        expect(page.locator('.garage-photo-editor')).to_have_count(0)
        assert state['uploads']==0
        first.get_by_role('button',name='+ Добавить фото',exact=True).click()
        first.locator('input[type=file]').set_input_files(dict(name='bike.png',mimeType='image/png',buffer=photo))
        first.get_by_role('button',name='Сохранить фото').click()
        expect(first.get_by_role('alert')).to_contain_text('Try again')
        first.get_by_role('button',name='Сохранить фото').click()
        expect(first.locator('img.bike-photo')).to_have_attribute('src','/media/saved.png')
        expect(first.get_by_role('button',name='Изменить фото',exact=True)).to_be_visible()
        assert state['uploads']==2
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        Path('output/garage-design').mkdir(parents=True,exist_ok=True)
        page.evaluate('scrollTo(0,0)');page.screenshot(path=f'output/garage-design/garage-{width}.png',full_page=True)
        state['empty']=True;page.reload()
        expect(page.get_by_role('link',name='Добавить первый велосипед',exact=True)).to_be_visible()
        assert not errors,errors
        print(f'PASS {width}px: placeholder, photo, collapsed upload, cancel, retry, refresh, empty state and width')
        context.close()
    browser.close()
