from datetime import datetime, timezone

from posts.post_entity import Post


class PostStorage:
    """In-memory storage for posts"""
    
    def __init__(self):
        self.posts: list[Post] = []
        self._next_id = 1
    
    async def create(self, post: Post) -> Post:
        """Create a new post"""
        if post.id == 0:
            post.id = self._next_id
            self._next_id += 1
        self.posts.append(post)
        return post
    
    async def get_all(self, limit: int = 20, offset: int = 0) -> list[Post]:
        """Get all posts with pagination (US4)"""
        # Sort by created_at descending (newest first)
        sorted_posts = sorted(self.posts, key=lambda p: p.created_at, reverse=True)
        return sorted_posts[offset:offset + limit]
    
    async def get_by_id(self, post_id: int) -> Post | None:
        """Get post by ID"""
        for post in self.posts:
            if post.id == post_id:
                return post
        return None
    
    async def get_by_author(self, author_id: int) -> list[Post]:
        """Get posts by author"""
        return [p for p in self.posts if p.author_id == author_id]
