import type { PostCategory } from '../types';

// Categories
export const POST_CATEGORIES: PostCategory[] = [
  'маршрут',
  'обслуживание',
  'апгрейд',
  'трюки',
];

// Category labels for display
export const CATEGORY_LABELS: Record<PostCategory, string> = {
  'обслуживание': 'Обслуживание',
  'апгрейд': 'Апгрейд',
  'маршрут': 'Маршруты',
  'трюки': 'Трюки',
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
