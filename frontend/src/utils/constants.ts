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

// Pagination
export const POSTS_PER_PAGE = 20;

// Form validation
export const MIN_USERNAME_LENGTH = 3;
export const MIN_PASSWORD_LENGTH = 6;
export const MAX_USERNAME_LENGTH = 50;
export const MAX_BIO_LENGTH = 1000;
export const MAX_POST_TITLE_LENGTH = 200;
export const MAX_POST_TEXT_LENGTH = 5000;

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
  SAVED: '/saved',
} as const;
