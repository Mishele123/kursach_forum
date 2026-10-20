// User types
export interface User {
  id: number;
  username: string;
  email?: string;
  role: 'USER' | 'MODERATOR' | 'ADMIN';
  avatar_url?: string;
  bio?: string;
  city?: string;
  discipline?: string;
  interests?: string;
  created_at: string;
}

export interface CreateUserDto {
  username: string;
  password: string;
}

export interface LoginDto {
  username: string;
  password: string;
}

export interface UpdateUserDto {
  city?: string;
  discipline?: string;
  interests?: string;
  bio?: string;
}

// Post types
export type PostCategory = 'обслуживание' | 'апгрейд' | 'маршрут' | 'трюки';

export interface Post {
  id: number;
  title: string;
  text: string;
  category: PostCategory;
  photo_url?: string;
  author_id: number;
  author_username?: string;
  created_at: string;
}

export interface CreatePostDto {
  title: string;
  text: string;
  category: PostCategory;
  photo_url?: string;
}

// Bike types
export interface Bike {
  id: number;
  brand: string;
  model: string;
  year: number;
  user_id: number;
  created_at: string;
}

export interface CreateBikeDto {
  brand: string;
  model: string;
  year: number;
}

// Auth response
export interface AuthResponse {
  message: string;
  user: User;
}
