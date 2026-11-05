"""Gallery operations. Mutations require the parent post row lock."""
from fastapi import HTTPException
from sqlalchemy import select
from community.models import PostPhoto
from community.schemas import PhotoResponse
from community.media import receive_photo, remove_photo

MAX_POST_PHOTOS = 10


async def attach_photos(db, items):
    if not items:
        return
    by_id = {item.id: item for item in items}
    for item in items:
        item.photos = []
        item.photo_url = None
    photos = await db.scalars(select(PostPhoto).where(PostPhoto.post_id.in_(by_id)).order_by(PostPhoto.id))
    for photo in photos:
        by_id[photo.post_id].photos.append(PhotoResponse(id=photo.id, url=f'/media/{photo.filename}'))
    for item in items:
        if item.photos:
            item.photo_url = item.photos[0].url


async def save_batch(files, directory):
    if not 1 <= len(files) <= MAX_POST_PHOTOS:
        raise HTTPException(422, 'В одном запросе должно быть от 1 до 10 фотографий')
    filenames = []
    try:
        for file in files:
            filenames.append(await receive_photo(file, directory))
    except BaseException:
        for filename in filenames:
            remove_photo(directory, filename)
        raise
    return filenames
