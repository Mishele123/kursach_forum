"""Browser acceptance check for all five Sprint 1 stories.
Creates a unique account per viewport and removes only that account afterwards.
The application and DATABASE_URL must point to the same local PostgreSQL database.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from PIL import Image
from playwright.sync_api import sync_playwright, expect
from sqlalchemy import delete
from database import Database
from models import UserRow


async def remove_test_account(username):
    if not username.startswith("sprint1_ui_"):
        raise RuntimeError("Refusing to remove a non-test account")
    database = Database()
    try:
        async with database.session() as session:
            await session.execute(delete(UserRow).where(UserRow.username == username))
    finally:
        await database.close()


def check(browser, base_url, width, height, output):
    username = "sprint1_ui_" + uuid.uuid4().hex[:12]
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    upload_path = None
    avatar_path = None
    bike_path = None
    renamed = username + "_new"
    try:
        page.goto(base_url + "/register")
        page.get_by_label("Имя пользователя", exact=True).fill(username)
        page.get_by_label("Email", exact=True).fill(username + "@example.com")
        page.get_by_label("Пароль", exact=True).fill("SprintOne123!")
        page.get_by_label("Подтвердите пароль", exact=True).fill("SprintOne123!")
        page.get_by_role("button", name="Создать аккаунт", exact=True).click()
        page.wait_for_url("**/feed")
        expect(page.locator(".velo-header .logo")).to_have_text("velo.")
        page.goto(base_url + "/profile/edit")
        page.get_by_label("Имя пользователя", exact=True).fill(renamed)
        avatar = io.BytesIO()
        Image.new("RGB", (80, 80), "#246b50").save(avatar, "PNG")
        page.get_by_label("Фото профиля", exact=True).set_input_files({"name":"avatar.png", "mimeType":"image/png", "buffer":avatar.getvalue()})
        expect(page.locator(".profile-avatar-editor img")).to_be_visible()
        page.get_by_label("Город", exact=True).fill("Самара")
        page.get_by_label("Дисциплина", exact=True).fill("MTB")
        page.get_by_label("Интересы", exact=True).fill("Маршруты, велопутешествия")
        page.get_by_label("О себе", exact=True).fill("Проверка первого спринта")
        with page.expect_response(lambda response: response.url.endswith("/uploads") and response.request.method == "POST") as avatar_uploaded:
            page.get_by_role("button", name="Сохранить изменения", exact=True).click()
        avatar_path = avatar_uploaded.value.json()["url"]
        page.wait_for_url("**/profile")
        expect(page.locator(".velo-main")).to_contain_text("Самара")
        expect(page.locator(".velo-main h2").first).to_have_text(renamed)
        expect(page.locator(".velo-header .avatar img")).to_have_attribute("src", avatar_path)
        page.reload()
        expect(page.locator(".velo-header .avatar img")).to_have_attribute("src", avatar_path)
        page.goto(base_url + "/bikes/add")
        page.get_by_label("Бренд *", exact=True).fill("Trek")
        page.get_by_label("Модель *", exact=True).fill("Marlin 7")
        page.get_by_label("Год выпуска *", exact=True).fill("2023")
        bike_image = {"name":"bike.png", "mimeType":"image/png", "buffer":avatar.getvalue()}
        page.get_by_label("Фото велосипеда", exact=True).set_input_files({"name":"bad.txt", "mimeType":"text/plain", "buffer":b"not an image"})
        expect(page.get_by_role("alert")).to_be_visible()
        page.get_by_label("Фото велосипеда", exact=True).set_input_files(bike_image)
        expect(page.get_by_alt_text("Предпросмотр велосипеда")).to_be_visible()
        page.get_by_role("button", name="Убрать фотографию", exact=True).click()
        expect(page.get_by_alt_text("Предпросмотр велосипеда")).to_have_count(0)
        page.get_by_label("Фото велосипеда", exact=True).set_input_files(bike_image)
        with page.expect_response(lambda response: response.url.endswith("/uploads") and response.request.method == "POST") as bike_uploaded:
            page.get_by_role("button", name="Добавить велосипед", exact=True).click()
        bike_path = bike_uploaded.value.json()["url"]
        page.wait_for_url("**/bikes")
        expect(page.locator(".bike-grid")).to_contain_text("Trek Marlin 7")
        expect(page.locator(".bike-grid .bike-photo")).to_have_attribute("src", bike_path)
        page.reload()
        expect(page.locator(".bike-grid .bike-photo")).to_have_attribute("src", bike_path)
        page.wait_for_function("() => document.querySelector('.bike-grid .bike-photo')?.naturalWidth > 0")
        page.screenshot(path=str(output / f"bikes-{width}.png"), full_page=True)
        page.goto(base_url + "/post/create")
        title = "Велопрогулка " + username
        page.get_by_label("Заголовок *", exact=True).fill(title)
        page.get_by_label("Текст публикации *", exact=True).fill("**Лесные тропы** и *новые открытия*.")
        buffer = io.BytesIO()
        Image.new("RGB", (60, 40), "#246b50").save(buffer, "PNG")
        page.get_by_label("+ Добавьте одну фотографию", exact=True).set_input_files({"name":"ride.png", "mimeType":"image/png", "buffer":buffer.getvalue()})
        expect(page.get_by_alt_text("Предпросмотр фотографии")).to_be_visible()
        with page.expect_response(lambda response: response.url.endswith("/uploads") and response.request.method == "POST") as uploaded:
            page.get_by_role("button", name="Опубликовать", exact=True).click()
        upload_path = uploaded.value.json()["url"]
        page.wait_for_url("**/feed")
        card = page.locator(".post-card").filter(has=page.get_by_role("heading", name=title, exact=True))
        expect(card).to_be_visible()
        expect(card.locator(".post-author .avatar img")).to_have_attribute("src", avatar_path)
        expect(card.locator("strong").filter(has_text="Лесные тропы")).to_be_visible()
        expect(card.get_by_alt_text(title)).to_be_visible()
        page.screenshot(path=str(output / f"feed-{width}.png"), full_page=True)
        card.get_by_role("heading", name=title, exact=True).click()
        page.wait_for_url("**/post/*")
        expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible()
        page.goto(base_url + "/profile")
        page.get_by_role("button", name="Выйти из аккаунта", exact=True).click()
        page.wait_for_url("**/login")
        page.get_by_label("Email", exact=True).fill(username + "@example.com")
        page.get_by_label("Пароль", exact=True).fill("SprintOne123!")
        page.get_by_role("button", name="Войти", exact=True).click()
        page.wait_for_url("**/feed")
        page.reload()
        expect(page.locator(".velo-header .avatar")).to_be_visible()
        page.goto(base_url + "/profile")
        expect(page.locator(".velo-main")).to_contain_text("Trek Marlin 7")
        expect(page.locator(".profile-bike .bike-photo")).to_have_attribute("src", bike_path)
        expect(page.locator(".velo-main h2").first).to_have_text(renamed)
        expect(page.locator(".velo-header .avatar img")).to_have_attribute("src", avatar_path)
        page.goto(base_url + "/profile/edit")
        page.get_by_role("button", name="Убрать фото", exact=True).click()
        page.get_by_role("button", name="Сохранить изменения", exact=True).click()
        page.wait_for_url("**/profile")
        expect(page.locator(".velo-header .avatar img")).to_have_count(0)
        page.get_by_role("button", name="Выйти из аккаунта", exact=True).click()
        page.wait_for_url("**/login")
        if errors:
            raise AssertionError(errors)
        print(f"PASS: {width}px registration, rename, avatar upload/removal, bike photo, photo post, detail, login, session reload and logout")
    finally:
        context.close()
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(lambda: asyncio.run(remove_test_account(username))).result()
            executor.submit(lambda: asyncio.run(remove_test_account(renamed))).result()
        for path in [upload_path, avatar_path, bike_path]:
            if not path:
                continue
            name = Path(path).name
            if name.endswith(".png"):
                from shared.upload import UPLOAD_DIR
                (UPLOAD_DIR / name).unlink(missing_ok=True)


if __name__ == "__main__":
    base = os.environ.get("VELO_UI_URL", "http://127.0.0.1:8080")
    output = Path("test-results")
    output.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        channel = os.environ.get("PLAYWRIGHT_CHANNEL", "msedge" if sys.platform == "win32" else "chromium")
        browser = playwright.chromium.launch(channel=channel, headless=True)
        try:
            for width, height in [(1440, 1000), (390, 844)]:
                check(browser, base, width, height, output)
        finally:
            browser.close()
