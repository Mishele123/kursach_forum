import axios from 'axios';
import type { 
  User, 
  CreateUserDto, 
  LoginDto, 
  UpdateUserDto,
  AuthResponse,
  Post,
  CreatePostDto,
  Bike,
  CreateBikeDto
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth API
export const authApi = {
  register: async (data: CreateUserDto): Promise<User> => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  login: async (data: LoginDto): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  updateProfile: async (data: UpdateUserDto): Promise<User> => {
    const response = await api.put<User>('/auth/me', data);
    return response.data;
  },
};

// Posts API
export const postsApi = {
  getPosts: async (limit: number = 20, offset: number = 0): Promise<Post[]> => {
    const response = await api.get<Post[]>('/posts', {
      params: { limit, offset },
    });
    return response.data;
  },

  getPost: async (postId: number): Promise<Post> => {
    const response = await api.get<Post>(`/posts/${postId}`);
    return response.data;
  },

  createPost: async (data: CreatePostDto): Promise<Post> => {
    const response = await api.post<Post>('/posts', data);
    return response.data;
  },
};

// Bikes API
export const bikesApi = {
  getMyBikes: async (): Promise<Bike[]> => {
    const response = await api.get<Bike[]>('/bikes/my-bikes');
    return response.data;
  },

  createBike: async (data: CreateBikeDto): Promise<Bike> => {
    const response = await api.post<Bike>('/bikes', data);
    return response.data;
  },
};

export default api;

export function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map(item => item.msg).join('; ');
  }
  return 'Не удалось выполнить запрос. Проверьте подключение и попробуйте снова.';
}

export const uploadPhoto = async (file: File): Promise<string> => {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/uploads', form, { headers: { 'Content-Type': 'multipart/form-data' } });
  return data.url;
};
