import axios from 'axios';
import type { PeoplePage, PeopleFilters, PublicProfile } from '../types';
import type { Comment, CommentsPage, User, CreateUserDto, LoginDto, UpdateUserDto, AuthResponse, Post, CreatePostDto, Bike, CreateBikeDto, FeedResponse } from '../types';
const baseURL = import.meta.env.VITE_API_URL || '/api';
const api = axios.create({ baseURL, withCredentials: true });
export const authApi = {
 register: async (data: CreateUserDto) => (await api.post<{username:string}>('/auth/register',data)).data,
 login: async (data: LoginDto) => (await api.post<AuthResponse>('/auth/login',data)).data,
 getCurrentUser: async () => (await api.get<User>('/auth/me')).data,
 updateProfile: async (data: UpdateUserDto) => (await api.patch<User>('/users/me',data)).data,
 updateUsername: async (username: string) => (await api.patch<User>('/users/me/username', {username})).data,
 changePassword: async (current_password: string, new_password: string) => { await api.put('/auth/password', {current_password, new_password}); },
 uploadAvatar: async (file: File) => { const form = new FormData(); form.append('file', file); return (await api.put<User>('/users/me/avatar', form)).data; },
};
export const postsApi = {
 getPosts: async (limit=10, cursor?: string, filters: {q?: string; category?: string} = {}) => (await api.get<FeedResponse>('/posts',{params:{limit,cursor,...filters}})).data,
 setLike: async (id: number, enabled: boolean) => (await api.request<{like_count: number; liked_by_me: boolean}>({url: `/posts/${id}/like`, method: enabled ? 'PUT' : 'DELETE'})).data,
 createWithPhotos: async (data: CreatePostDto, files: File[]) => { const form = new FormData(); Object.entries(data).forEach(([key,value]) => form.append(key,value)); files.forEach(file => form.append('files',file)); return (await api.post<Post>('/posts/with-photos',form)).data; },
 addPhotos: async (id: number, files: File[]) => { const form = new FormData(); files.forEach(file => form.append('files',file)); return (await api.post<Post>(`/posts/${id}/photos`,form)).data; },
 getPost: async (id:number) => (await api.get<Post>(`/posts/${id}`)).data,
 createPost: async (data:CreatePostDto) => (await api.post<Post>('/posts',data)).data,
};
export const bikesApi = {
 getMyBikes: async () => (await api.get<Bike[]>('/users/me/bikes')).data,
 createBike: async (data:CreateBikeDto) => (await api.post<Bike>('/users/me/bikes',data)).data,
 uploadPhoto: async (id: number, file: File) => { const form = new FormData(); form.append('file',file); return (await api.put<Bike>(`/users/me/bikes/${id}/photo`,form)).data; },
};
export const peopleApi = {
 search: async (filters: PeopleFilters, cursor?: number) => (await api.get<PeoplePage>('/users', {params: {...filters, cursor, limit: 12}})).data,
 profile: async (id: number) => (await api.get<PublicProfile>(`/users/${id}`)).data,
 posts: async (id: number, cursor?: string) => (await api.get<FeedResponse>(`/users/${id}/posts`, {params: {cursor, limit: 10}})).data,
};
export function mediaUrl(path:string):string {
 if (/^https?:\/\//i.test(baseURL)) return new URL(path,baseURL).href;
 return path;
}
export function errorMessage(error:unknown):string {
 if(axios.isAxiosError(error)) { const detail=error.response?.data?.detail;
 if(typeof detail==='string') return detail;
 if(Array.isArray(detail)) return detail.map(item=>item.msg).join('; ');
 }
 return 'Не удалось выполнить запрос. Проверьте подключение и попробуйте снова.';
}
export default api;

export const commentsApi = {
 getComments: async (postId: number, cursor?: number) => (await api.get<CommentsPage>(`/posts/${postId}/comments`, {params: {limit: 10, cursor}})).data,
 createComment: async (postId: number, text: string) => (await api.post<Comment>(`/posts/${postId}/comments`, {text})).data,
};
