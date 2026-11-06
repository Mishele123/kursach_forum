export interface PublicUser { id: number; username: string; avatar_url: string | null; city: string | null; discipline: string | null; interests: string[]; }
export interface User extends PublicUser { email: string | null; bio: string | null; created_at: string; }
export interface PublicProfile extends PublicUser { bikes: Bike[]; }
export interface PeoplePage { items: PublicUser[]; next_cursor: number | null; }
export interface PeopleFilters { city?: string; discipline?: string; brand?: string; model?: string; }
export interface CreateUserDto { email: string; username: string; password: string; }
export interface LoginDto { email: string; password: string; remember_me?: boolean; }
export interface UpdateUserDto { city?: string | null; discipline?: string | null; interests?: string[]; bio?: string | null; }
export type PostCategory = 'maintenance' | 'upgrade' | 'route' | 'tricks';
export interface Author { id: number; username: string; avatar_url: string | null; }
export interface Post { id: number; title: string; text: string; category: PostCategory; photo_url: string | null; photos: {id: number; url: string}[]; like_count: number; liked_by_me: boolean; author: Author; created_at: string; }
export interface FeedResponse { items: Post[]; next_cursor: string | null; }
export interface CreatePostDto { title: string; text: string; category: PostCategory; }
export interface Bike { id: number; brand: string; model: string; year: number; photo_url: string | null; }
export interface CreateBikeDto { brand: string; model: string; year: number; }
export interface AuthResponse { username: string; }

export interface Comment { id: number; post_id: number; author: Author; text: string; created_at: string; }
export interface CommentsPage { items: Comment[]; next_cursor: number | null; }
