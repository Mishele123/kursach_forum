import type { PostCategory } from '../types';

// Categories
export const POST_CATEGORIES: PostCategory[] = [
  'route',
  'maintenance',
  'upgrade',
  'tricks',
];

// Category labels for display
export const CATEGORY_LABELS: Record<PostCategory, string> = {
  'maintenance': 'Обслуживание',
  'upgrade': 'Апгрейд',
  'route': 'Маршруты',
  'tricks': 'Трюки',
};

// Routes
export const ROUTES = {
  HOME: '/',
  FEED: '/feed',
  PROFILE: '/profile',
  MY_BIKES: '/bikes',
  ADD_BIKE: '/bikes/add',
  CREATE_POST: '/post/create',
  POST_DETAIL: '/post/:id',
  EDIT_PROFILE: '/profile/edit',
  LOGIN: '/login',
  REGISTER: '/register',
} as const;
