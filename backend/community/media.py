from io import BytesIO
from pathlib import Path
import secrets
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError
from fastapi import HTTPException

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 20_000_000


def save_photo(data: bytes, directory: Path) -> str:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as image:
                if image.format not in {'JPEG', 'PNG'}:
                    raise HTTPException(415, 'Допустимы только JPEG и PNG')
                if image.width * image.height > MAX_PIXELS:
                    raise HTTPException(413, 'Фотография превышает 20 мегапикселей')
                image.verify()
            with Image.open(BytesIO(data)) as image:
                image.load()
                clean = ImageOps.exif_transpose(image).convert('RGB')
                # Re-encode pixels only: do not retain metadata or appended content.
                output = BytesIO()
                clean.save(output, format='JPEG', quality=90)
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(413, 'Слишком большое разрешение фотографии')
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        raise HTTPException(415, 'Файл не является корректной фотографией')
    filename = secrets.token_hex(16) + '.jpg'
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    try:
        with path.open('xb') as file:
            file.write(output.getvalue())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return filename


async def receive_photo(file, directory: Path) -> str:
    from starlette.concurrency import run_in_threadpool
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, 'Максимальный размер фотографии — 5 МБ')
    return await run_in_threadpool(save_photo, data, directory)


def remove_photo(directory: Path, filename: str | None) -> None:
    import re
    # Never follow arbitrary paths or delete externally hosted legacy avatars.
    if filename and re.fullmatch(r'[0-9a-f]{32}\.jpg', filename):
        (directory / filename).unlink(missing_ok=True)
