"""Check profile settings against a mocked API without changing user data."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    for width in (1440, 390):
        user = dict(id=1, username='Minhhh', avatar_url=None, email='rider@example.com', city='Самара', discipline='Гравел', interests=['Гравел'], bio='Люблю новые маршруты.', created_at='2026-11-01T10:00:00Z')
        writes = []
        context = browser.new_context(viewport=dict(width=width, height=1080))
        def api(route):
            path = route.request.url.split('/api/')[-1]
            if path == 'users/me' and route.request.method == 'PATCH':
                data = route.request.post_data_json
                writes.append(data)
                user.update(data)
                return route.fulfill(json=user)
            if path == 'auth/me': return route.fulfill(json=user)
            if path == 'users/me/bikes': return route.fulfill(json=[])
            return route.fulfill(json={})
        context.route('**/api/**', api)
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://localhost:5173/profile/edit')
        expect(page.get_by_role('heading', name='Настройки профиля')).to_be_visible()
        save = page.get_by_role('button', name='Сохранить изменения', exact=True)
        expect(save).to_be_disabled()
        page.get_by_label('Город', exact=True).fill('Казань')
        expect(page.locator('.preview-city')).to_contain_text('Казань')
        page.get_by_role('button', name='Путешествия', exact=True).click()
        expect(page.locator('.preview-interests')).to_contain_text('Путешествия')
        expect(page.get_by_role('button', name='Аккаунт', exact=True)).to_have_count(0)
        expect(page.locator('#account-name')).to_have_count(0)
        expect(page.locator('#account-security')).not_to_be_visible()
        page.get_by_role('button', name='Смена пароля', exact=True).click()
        expect(page.locator('#account-security')).to_be_visible()
        expect(page.locator('#account-name')).not_to_be_visible()
        page.get_by_role('button', name='Профиль', exact=True).click()
        expect(page.get_by_label('Город', exact=True)).to_have_value('Казань')
        page.get_by_role('button', name='Отмена', exact=True).click()
        expect(page.get_by_label('Город', exact=True)).to_have_value('Самара')
        page.get_by_label('Город', exact=True).fill('Казань')
        save.click()
        expect(page.locator('.save-status')).to_have_text('Изменения сохранены')
        assert writes == [dict(city='Казань', discipline='Гравел', bio='Люблю новые маршруты.', interests=['Гравел'])], writes
        expect(save).to_be_disabled()
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Horizontal overflow'
        assert not errors, errors
        output = Path('output/profile-design')
        output.mkdir(parents=True, exist_ok=True)
        page.evaluate('window.scrollTo(0, 0)')
        page.screenshot(path=str(output / f'profile-{width}.png'), full_page=True)
        context.close()
        print(f'PASS {width}px: preview, tabs, draft preservation, cancel, save payload and responsive width')
    browser.close()



