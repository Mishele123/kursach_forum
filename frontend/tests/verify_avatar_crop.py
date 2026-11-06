"""Avatar crop interaction and exported pixels, with mocked API and no database writes."""
import io
import json
import re
import threading
from email.parser import BytesParser
from email.policy import default
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
from playwright.sync_api import sync_playwright, expect
from verify_main_contract import SPA


def check(browser,base,width):
    user=dict(id=1,username='rider',avatar_url=None,email='rider@example.com',city=None,discipline=None,interests=[],bio=None,created_at='2026-11-01T10:00:00Z')
    state=dict(uploads=0,fail=True)
    image=Image.new('RGB',(800,400))
    for x in range(800):
        image.paste((int(x*255/799),40,255-int(x*255/799)),(x,0,x+1,400))
    buffer=io.BytesIO();image.save(buffer,'PNG')
    photo=dict(name='gradient.png',mimeType='image/png',buffer=buffer.getvalue())
    errors,failures=[],[]
    context=browser.new_context(viewport=dict(width=width,height=950))
    def api(route):
        req=route.request;url=urlparse(req.url);path=url.path.removeprefix('/api')
        if not url.netloc.endswith(':8000') and not url.path.startswith(('/api/','/media/')):return route.continue_()
        cors={'Access-Control-Allow-Origin':base,'Access-Control-Allow-Credentials':'true','Access-Control-Allow-Headers':'content-type','Access-Control-Allow-Methods':'GET, PUT, OPTIONS'}
        if req.method=='OPTIONS':return route.fulfill(status=204,headers=cors)
        if path.startswith('/media/'):return route.fulfill(status=200,content_type='image/png',body=buffer.getvalue())
        status,result=200,None
        try:
            if path=='/auth/me':result=user
            elif path=='/users/me/bikes':result=[]
            elif path=='/users/me/avatar':
                state['uploads']+=1
                assert req.method=='PUT'
                message=BytesParser(policy=default).parsebytes(('Content-Type: '+req.headers['content-type']+'\r\nMIME-Version: 1.0\r\n\r\n').encode()+req.post_data_buffer)
                parts=list(message.iter_parts())
                assert len(parts)==1 and parts[0].get_param('name',header='content-disposition')=='file'
                cropped=Image.open(io.BytesIO(parts[0].get_payload(decode=True)))
                assert cropped.format=='JPEG' and cropped.size==(512,512)
                assert cropped.getpixel((256,256))[0]<120, 'Pan/zoom must affect exported crop pixels'
                if state['fail']:state['fail']=False;status,result=503,dict(detail='Повторите загрузку')
                else:user['avatar_url']='/media/saved.jpg';result=user
            else:raise AssertionError(f'Unexpected API {req.method} {path}')
        except Exception as error:failures.append(str(error));status,result=500,dict(detail=str(error))
        route.fulfill(status=status,content_type='application/json',body=json.dumps(result),headers=cors)
    context.route('**/*',api)
    page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(base+'/profile/edit')
    panel=page.locator('#account-avatar')
    picker=panel.get_by_role('button',name='Добавить фото',exact=True)
    expect(picker).to_be_visible()
    expect(panel.get_by_role('button',name='Сохранить аватар',exact=True)).to_have_count(0)
    field=panel.locator('input[type=file]')
    field.set_input_files(dict(name='bad.png',mimeType='image/png',buffer=b'invalid'))
    expect(panel.get_by_role('alert')).to_contain_text('корректный')
    field.set_input_files(dict(name='big.png',mimeType='image/png',buffer=b'x'*(5*1024*1024+1)))
    expect(panel.get_by_role('alert')).to_contain_text('до 5 МБ')
    huge=io.BytesIO();Image.new('RGB',(4500,4500)).save(huge,'PNG')
    field.set_input_files(dict(name='huge.png',mimeType='image/png',buffer=huge.getvalue()))
    expect(panel.get_by_role('alert')).to_contain_text('20 мегапикселей')
    with page.expect_file_chooser() as chooser:picker.click()
    chooser.value.set_files(photo)
    modal=page.get_by_role('dialog',name='Настроить фото')
    expect(modal).to_be_visible()
    assert state['uploads']==0
    page.keyboard.press('Escape')
    expect(modal).not_to_be_visible()
    expect(picker).to_be_focused()
    field.set_input_files(photo)
    expect(modal).to_be_visible()
    modal.get_by_role('button',name='Увеличить фото',exact=True).click()
    zoom=modal.get_by_label('Масштаб',exact=True)
    expect(zoom).to_have_value('1.1')
    zoom.focus();zoom.press('ArrowRight')
    stage=modal.get_by_role('group',name='Область кадрирования фото')
    stage.focus();stage.press('ArrowRight')
    box=stage.bounding_box()
    page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2)
    page.mouse.down();page.mouse.move(box['x']+box['width']/2+40,box['y']+box['height']/2,steps=6);page.mouse.up()
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
    page.screenshot(path=str(Path(__file__).parent/'artifacts'/f'avatar-crop-{width}.png'),full_page=True)
    modal.get_by_role('button',name='Применить',exact=True).click()
    expect(modal).not_to_be_visible()
    expect(panel.locator('.avatar-preview-badge')).to_have_text('Предпросмотр')
    expect(panel.locator('.avatar-crop-preview img')).to_have_attribute('src',re.compile('^blob:'))
    assert state['uploads']==0
    panel.get_by_role('button',name='Выбрать другое фото',exact=True).click()
    # Canceling the chooser itself leaves the pending crop intact.
    field.set_input_files(photo)
    expect(modal).to_be_visible();page.keyboard.press('Escape')
    expect(panel.locator('.avatar-preview-badge')).to_be_visible()
    panel.get_by_role('button',name='Сохранить аватар',exact=True).click()
    expect(panel.get_by_role('alert')).to_contain_text('Повторите загрузку')
    expect(panel.locator('.avatar-preview-badge')).to_be_visible()
    panel.get_by_role('button',name='Сохранить аватар',exact=True).click()
    expect(panel.get_by_role('status')).to_have_text('Аватар сохранён')
    expect(panel.locator('.avatar-crop-preview img')).to_have_attribute('src',re.compile('/media/saved[.]jpg$'))
    expect(page.locator('.velo-header .avatar img')).to_have_attribute('src',re.compile('/media/saved[.]jpg$'))
    assert state['uploads']==2
    field.set_input_files(photo);expect(modal).to_be_visible()
    modal.get_by_role('button',name='Применить',exact=True).click()
    expect(modal).not_to_be_visible()
    panel.get_by_role('button',name='Отмена',exact=True).click()
    expect(panel.get_by_role('button',name='Сохранить аватар',exact=True)).to_have_count(0)
    assert state['uploads']==2
    assert not errors,errors
    assert not failures,failures
    context.close()
    print(f'PASS {width}px: validation, dialog/cancel, mouse and keyboard pan/zoom, exported 512px crop, explicit save, retry and avatar refresh')


if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SPA,directory=str(Path(__file__).resolve().parents[1]/'dist')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(channel='msedge',headless=True)
            for width in (1440,390):check(browser,f'http://127.0.0.1:{server.server_port}',width)
            browser.close()
    finally:server.shutdown()
