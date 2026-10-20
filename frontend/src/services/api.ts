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

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth API
export const authApi = {
  register: async (data: CreateUserDto): Promise<User> => {
    const response = await api.post<User>('/register', data);
    return response.data;
  },

  login: async (data: LoginDto): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/login', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/me');
    return response.data;
  },

  updateProfile: async (data: UpdateUserDto): Promise<User> => {
    const response = await api.put<User>('/me', data);
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
