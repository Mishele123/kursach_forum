import axios from 'axios';
import type { User, CreateUserDto, LoginDto, UpdateUserDto, AuthResponse, Post, CreatePostDto, Bike, CreateBikeDto, FeedResponse } from '../types';
const baseURL = import.meta.env.VITE_API_URL || '/api';
const api = axios.create({ baseURL, withCredentials: true });
export const authApi = {
 register: async (data: CreateUserDto) => (await api.post<{username:string}>('/auth/register',data)).data,
 login: async (data: LoginDto) => (await api.post<AuthResponse>('/auth/login',data)).data,
 getCurrentUser: async () => (await api.get<User>('/auth/me')).data,
 updateProfile: async (data: UpdateUserDto) => (await api.patch<User>('/users/me',data)).data,
};
export const postsApi = {
 getPosts: async (limit=10, cursor?: string) => (await api.get<FeedResponse>('/posts',{params:{limit,cursor}})).data,
 getPost: async (id:number) => (await api.get<Post>(`/posts/${id}`)).data,
 createPost: async (data:CreatePostDto) => (await api.post<Post>('/posts',data)).data,
 uploadPhoto: async (id:number,file:File) => { const form=new FormData(); form.append('file',file); return (await api.put<Post>(`/posts/${id}/photo`,form)).data; },
};
export const bikesApi = {
 getMyBikes: async () => (await api.get<Bike[]>('/users/me/bikes')).data,
 createBike: async (data:CreateBikeDto) => (await api.post<Bike>('/users/me/bikes',data)).data,
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
