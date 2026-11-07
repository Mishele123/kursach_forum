from playwright.sync_api import sync_playwright, expect
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    for width in (1440,390):
        context=browser.new_context(viewport=dict(width=width,height=950))
        def api(route):
            path=route.request.url.split('/api')[-1].split('?')[0]
            if path=='/auth/me':return route.fulfill(status=401,json={})
            if path=='/users/7':return route.fulfill(json=dict(id=7,username='rider',avatar_url=None,city='Самара',discipline='Гравел',interests=['Город','Путешествия'],bikes=[dict(id=1,brand='Trek',model='Marlin',year=2024,photo_url=None)]))
            if path=='/users/7/posts':return route.fulfill(json=dict(items=[],next_cursor=None))
            return route.fulfill(json={})
        context.route('**/api/**',api)
        page=context.new_page();errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://localhost:5173/users/7')
        expect(page.locator('#public-user-name')).to_have_text('rider')
        expect(page.locator('.profile-inline-interests li')).to_have_count(2)
        expect(page.locator('.profile-bike-card')).to_have_count(1)
        expect(page.get_by_text('Публикаций пока нет.',exact=True)).to_be_visible()
        expect(page.locator('.profile-account-actions')).to_have_count(0)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors,errors
        print(f'PASS {width}px: public identity, interests, bikes, empty posts, no account controls, responsive width')
        context.close()
    browser.close()
