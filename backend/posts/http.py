from datetime import datetime, timezone

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Query

from auth.dependencies import CurrentUserId
from auth.user_interfaces import UserRepository
from posts.post_dto import CreatePostDto, PostResponseDto
from posts.post_entity import Post, PostCategory
from posts.post_storage import PostStorage

router = APIRouter(prefix="/posts", tags=["posts"], route_class=DishkaRoute)


@router.post("", status_code=201)
async def create_post(
    dto: CreatePostDto,
    author_id: CurrentUserId,
    post_storage: FromDishka[PostStorage],
    user_repo: FromDishka[UserRepository]
) -> PostResponseDto:
    """
    Create a new post (US3).
    
    Requires: Bearer token in Authorization header
    """
    # Verify user exists
    user = await user_repo.read(author_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if dto.photo_url:
        from pathlib import Path
        from urllib.parse import urlparse
        from shared.upload import UPLOAD_DIR
        filename = Path(urlparse(dto.photo_url).path).name
        if not filename.startswith(f"{author_id}_") or not (UPLOAD_DIR / filename).is_file():
            raise HTTPException(400, "Use an image uploaded by your account")
        dto.photo_url = f"/uploads/{filename}"

    # Create post
    post = Post(
        id=0,
        title=dto.title,
        text=dto.text,
        category=dto.category,
        photo_url=dto.photo_url,
        author_id=author_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    created_post = await post_storage.create(post)
    
    return PostResponseDto(
        id=created_post.id,
        title=created_post.title,
        text=created_post.text,
        category=created_post.category,
        photo_url=created_post.photo_url,
        author_id=created_post.author_id,
        author_username=user.username,
        author_avatar_url=user.avatar_url,
        created_at=created_post.created_at
    )


@router.get("")
async def get_posts(
    post_storage: FromDishka[PostStorage],
    user_repo: FromDishka[UserRepository],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: PostCategory | None = None,
    author_id: int | None = Query(None, ge=1),
    q: str | None = Query(None, max_length=200)
) -> list[PostResponseDto]:
    """Get posts feed with pagination (US4)"""
    return await post_storage.get_all(limit=limit, offset=offset, category=category, author_id=author_id, q=q)



@router.get("/{post_id}")
async def get_post(
    post_id: int,
    post_storage: FromDishka[PostStorage],
    user_repo: FromDishka[UserRepository]
) -> PostResponseDto:
    """Get a single post by ID"""
    post = await post_storage.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    author = await user_repo.read(post.author_id)
    
    return PostResponseDto(
        id=post.id,
        title=post.title,
        text=post.text,
        category=post.category,
        photo_url=post.photo_url,
        author_id=post.author_id,
        author_username=author.username if author else "Unknown",
        author_avatar_url=author.avatar_url if author else None,
        created_at=post.created_at
    )
