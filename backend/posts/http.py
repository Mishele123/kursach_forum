from datetime import datetime, timezone

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Query

from auth.user_interfaces import UserRepository
from posts.post_dto import CreatePostDto, PostResponseDto
from posts.post_entity import Post
from posts.post_storage import PostStorage

router = APIRouter(prefix="/posts", tags=["posts"], route_class=DishkaRoute)


@router.post("", status_code=201)
async def create_post(
    dto: CreatePostDto,
    post_storage: FromDishka[PostStorage],
    user_repo: FromDishka[UserRepository],
    author_id: int = 1  # Temporary: hardcoded (should come from JWT)
) -> PostResponseDto:
    """Create a new post (US3)"""
    # Verify user exists
    user = await user_repo.read(author_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
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
        created_at=created_post.created_at
    )


@router.get("")
async def get_posts(
    post_storage: FromDishka[PostStorage],
    user_repo: FromDishka[UserRepository],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> list[PostResponseDto]:
    """Get posts feed with pagination (US4)"""
    posts = await post_storage.get_all(limit=limit, offset=offset)
    
    # Enrich with author usernames
    result = []
    for post in posts:
        author = await user_repo.read(post.author_id)
        result.append(PostResponseDto(
            id=post.id,
            title=post.title,
            text=post.text,
            category=post.category,
            photo_url=post.photo_url,
            author_id=post.author_id,
            author_username=author.username if author else "Unknown",
            created_at=post.created_at
        ))
    
    return result


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
        created_at=post.created_at
    )
