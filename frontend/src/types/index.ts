export interface User { id: number; username: string; email: string | null; city: string | null; discipline: string | null; interests: string[]; bio: string | null; created_at: string; }
export interface CreateUserDto { email: string; username: string; password: string; }
export interface LoginDto { email: string; password: string; remember_me?: boolean; }
export interface UpdateUserDto { city?: string | null; discipline?: string | null; interests?: string[]; bio?: string | null; }
export type PostCategory = 'maintenance' | 'upgrade' | 'route' | 'tricks';
export interface Post { id: number; title: string; text: string; category: PostCategory; photo_url: string | null; author: { id: number; username: string }; created_at: string; }
export interface FeedResponse { items: Post[]; next_cursor: string | null; }
export interface CreatePostDto { title: string; text: string; category: PostCategory; }
export interface Bike { id: number; brand: string; model: string; year: number; }
export interface CreateBikeDto { brand: string; model: string; year: number; }
export interface AuthResponse { username: string; }
