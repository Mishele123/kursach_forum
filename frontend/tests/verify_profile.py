"""Profile layout and existing flows against isolated API fixtures. No backend writes."""
import io
import json
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
from playwright.sync_api import sync_playwright, expect
from verify_main_contract import SPA


def check(browser, base, width):
    user = dict(id=1,username='rider',avatar_url='/media/avatar.png',email='rider@example.com',
                city='Самара',discipline='MTB',interests=['Маршруты','Ремонт'],bio='На двух колёсах — вместе.',created_at='2026-11-01T10:00:00Z')
    bikes=[dict(id=1,brand='Trek',model='Marlin 7',year=2024,photo_url='/media/bike.png'),
           dict(id=2,brand='Giant',model='Escape',year=2023,photo_url=None)]
    state=dict(auth=True,fail_bikes=False,fail_upload=True,uploads=0,renames=0)
    image=io.BytesIO()
    Image.new('RGB',(640,360),'#80A999').save(image,'PNG')
    errors,failures=[],[]
    context=browser.new_context(viewport=dict(width=width,height=1000))

    def api(route):
        req=route.request
        parsed=urlparse(req.url)
        if not parsed.netloc.endswith(':8000') and not parsed.path.startswith(('/api/','/media/')):
            return route.continue_()
        path=parsed.path.removeprefix('/api')
        cors={'Access-Control-Allow-Origin':base,'Access-Control-Allow-Credentials':'true','Access-Control-Allow-Headers':'content-type','Access-Control-Allow-Methods':'GET, PUT, POST, OPTIONS'}
        if req.method=='OPTIONS':return route.fulfill(status=204,headers=cors)
        if path.startswith('/media/'):
            return route.fulfill(status=200,content_type='image/png',body=image.getvalue())
        status,result=200,None
        try:
            if path=='/auth/me':status,result=(200,user) if state['auth'] else (401,dict(detail='Unauthorized'))
            elif path=='/users/me/username':
                assert req.method=='PATCH'
                data=req.post_data_json
                assert set(data)=={'username'}
                state['renames']+=1
                if data['username']=='taken':status,result=409,dict(detail='Имя пользователя уже занято')
                else:user['username']=data['username'];result=user
            elif path=='/auth/logout':state['auth']=False;status=204
            elif path=='/users/me/bikes':
                status,result=(503,dict(detail='Temporary error')) if state['fail_bikes'] else (200,bikes)
            elif path=='/users/me/bikes/1/photo':
                assert req.method=='PUT' and 'multipart/form-data' in req.headers['content-type']
                state['uploads']+=1
                if state['fail_upload']:
                    state['fail_upload']=False
                    status,result=415,dict(detail='Ошибка фото')
                else:
                    bikes[0]['photo_url']='/media/replaced.png'
                    result=bikes[0]
            else:raise AssertionError(f'Unexpected API: {req.method} {path}')
        except Exception as error:
            failures.append(str(error));status,result=500,dict(detail=str(error))
        route.fulfill(status=status,content_type='application/json',body='' if status==204 else json.dumps(result),headers=cors)

    context.route('**/*',api)
    page=context.new_page()
    page.on('pageerror',lambda error: errors.append(str(error)))
    page.goto(base+'/profile')
    expect(page.get_by_role('heading',name='rider',exact=True)).to_be_visible()
    expect(page.locator('.interest-tags li')).to_have_count(2)
    expect(page.locator('.profile-bike-card')).to_have_count(2)
    expect(page.get_by_role('link',name='Редактировать профиль',exact=True)).to_have_attribute('href','/profile/edit')
    expect(page.locator('.profile-links a')).to_have_attribute('href','/users/1')
    expect(page.locator('.profile-garage').get_by_role('link',name='Добавить велосипед',exact=False)).to_have_attribute('href','/bikes/add')
    expect(page.locator('.profile-garage-link')).to_have_attribute('href','/bikes')
    if width>1150:
        expect(page.locator('.profile-checklist .complete')).to_have_count(4)
        expect(page.locator('.profile-aside .garage-card')).to_have_count(0)
    boxes=[page.locator('.profile-bike-media').nth(i).bounding_box() for i in range(2)]
    assert all(abs(box['width']/box['height']-16/9)<0.02 for box in boxes)
    assert (abs(boxes[0]['y']-boxes[1]['y'])<1) == (width>900)
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
    page.screenshot(path=str(Path(__file__).parent/'artifacts'/f'profile-{width}.png'),full_page=True)
    pencil=page.get_by_role('button',name='Изменить имя',exact=True)
    pencil.click()
    name=page.get_by_role('textbox',name='Новое имя пользователя',exact=True)
    expect(name).to_be_focused()
    name.fill('draft_name')
    name.press('Escape')
    expect(page.get_by_role('heading',name='rider',exact=True)).to_be_visible()
    expect(pencil).to_be_focused()
    assert state['renames']==0
    pencil.click()
    name.fill('bad name')
    page.get_by_role('button',name='Сохранить имя',exact=True).click()
    assert state['renames']==0
    name.fill('taken')
    name.press('Enter')
    expect(page.get_by_role('alert')).to_contain_text('уже занято')
    expect(name).to_have_value('taken')
    name.fill('renamed_rider')
    page.screenshot(path=str(Path(__file__).parent/'artifacts'/f'profile-edit-name-{width}.png'),full_page=True)
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), 'Inline editor overflow'
    page.get_by_role('button',name='Сохранить имя',exact=True).click()
    expect(page.get_by_role('heading',name='renamed_rider',exact=True)).to_be_visible()
    expect(pencil).to_be_focused()
    page.reload()
    expect(page.get_by_role('heading',name='renamed_rider',exact=True)).to_be_visible()
    pencil.click()
    name.fill('cancelled_name')
    page.get_by_role('button',name='Отменить изменение имени',exact=True).click()
    expect(page.get_by_role('heading',name='renamed_rider',exact=True)).to_be_visible()
    assert state['renames']==2
    first=page.locator('.profile-bike-card').first
    first.locator('summary').click()
    picker=first.get_by_role('button',name='Добавить фото',exact=True)
    expect(picker).to_be_visible()
    picker.scroll_into_view_if_needed()
    picker.focus()
    expect(picker).to_be_focused()
    with page.expect_file_chooser() as chooser:
        page.keyboard.press('Enter')
    chooser.value.set_files(dict(name='new-bike.png',mimeType='image/png',buffer=image.getvalue()))
    expect(first.locator('.photo-picker-filenames')).to_contain_text('new-bike.png')
    first.get_by_role('button',name='Сохранить фото',exact=True).click()
    expect(first.get_by_role('alert')).to_contain_text('Ошибка фото')
    first.get_by_role('button',name='Сохранить фото',exact=True).click()
    expect(page.locator('.profile-bike-card').first.locator('.bike-photo')).to_have_attribute('src', __import__('re').compile('/media/replaced[.]png$'))
    assert state['uploads']==2
    user['interests']=[];bikes.clear()
    page.reload()
    expect(page.locator('.profile-interests').get_by_role('link',name='+ Добавить',exact=True)).to_be_visible()
    expect(page.get_by_role('link',name='Добавить первый велосипед',exact=True)).to_be_visible()
    state['fail_bikes']=True
    page.reload()
    expect(page.get_by_role('alert')).to_contain_text('Не удалось загрузить велосипеды')
    state['fail_bikes']=False
    page.get_by_role('button',name='Повторить',exact=True).click()
    expect(page.get_by_role('link',name='Добавить первый велосипед',exact=True)).to_be_visible()
    page.get_by_role('button',name='Выйти из аккаунта',exact=True).click()
    page.wait_for_url('**/login')
    assert not failures,failures
    assert not errors,errors
    context.close()
    print(f'PASS {width}px: profile/tags, bike grid and 16:9, keyboard photo picker, upload retry, empty/error states, links and logout')


if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SPA,directory=str(Path(__file__).resolve().parents[1]/'dist')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(channel='msedge',headless=True)
            for width in (1440,768,390):check(browser,f'http://127.0.0.1:{server.server_port}',width)
            browser.close()
    finally:server.shutdown()
