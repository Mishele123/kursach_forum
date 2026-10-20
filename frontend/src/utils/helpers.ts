import type { PostCategory } from '../types';

// Format date to relative time (Russian)
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'только что';
  if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} ${getMinutesWord(minutes)} назад`;
  }
  if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} ${getHoursWord(hours)} назад`;
  }
  if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} ${getDaysWord(days)} назад`;
  }

  // If older than a week, show date
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
};

const getMinutesWord = (count: number): string => {
  if (count % 10 === 1 && count % 100 !== 11) return 'минуту';
  if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) return 'минуты';
  return 'минут';
};

const getHoursWord = (count: number): string => {
  if (count % 10 === 1 && count % 100 !== 11) return 'час';
  if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) return 'часа';
  return 'часов';
};

const getDaysWord = (count: number): string => {
  if (count % 10 === 1 && count % 100 !== 11) return 'день';
  if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) return 'дня';
  return 'дней';
};

// Get category color
export const getCategoryColor = (category: PostCategory): string => {
  const colors: Record<PostCategory, string> = {
    'обслуживание': 'bg-blue-500',
    'апгрейд': 'bg-purple-500',
    'маршрут': 'bg-green-500',
    'трюки': 'bg-red-500',
  };
  return colors[category] || 'bg-gray-500';
};

// Get category display name (already in Russian)
export const getCategoryDisplayName = (category: PostCategory): string => {
  return category.charAt(0).toUpperCase() + category.slice(1);
};

// Get user initials for avatar
export const getUserInitials = (username: string): string => {
  return username
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

// Validate email
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Truncate text
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};
