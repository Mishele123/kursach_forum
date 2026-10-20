import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePosts } from '../hooks';
import { PostCard } from '../components/posts';
import { Loading } from '../components/common';
import { useAuth } from '../context/AuthContext';
import { POST_CATEGORIES, CATEGORY_LABELS, ROUTES } from '../utils/constants';
import type { PostCategory } from '../types';

const FeedPage: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<PostCategory | 'all'>('all');
  const { posts, isLoading, error } = usePosts();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const filteredPosts = selectedCategory === 'all' 
    ? posts 
    : posts.filter(post => post.category === selectedCategory);

  if (isLoading) {
    return <Loading message="Загрузка публикаций..." />;
  }

  return (
    <div className="py-8 px-8 max-w-[856px]">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-[36px] font-bold text-gray-900 mb-2 leading-tight">
          Ближе к людям. Дальше на велосипеде.
        </h1>
        <p className="text-[15px] text-gray-600">
          Истории, опыт и новые открытия вашего сообщества
        </p>
      </div>

      {/* Quick Post Composer */}
      {isAuthenticated && (
        <div className="bg-white rounded-2xl p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-4 text-[17px]">Есть чем поделиться?</h3>
          <button
            onClick={() => navigate(ROUTES.CREATE_POST)}
            className="w-full px-4 py-3.5 bg-[#f5f3f0] hover:bg-gray-100 rounded-xl text-left text-gray-500 transition-colors mb-4 text-[15px]"
          >
            Маршрут, апгрейд или новая история...
          </button>
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-4 py-2 text-[14px] font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
              + Фото
            </button>
            <button className="flex items-center gap-2 px-4 py-2 text-[14px] font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
              Категория
            </button>
            <button
              onClick={() => navigate(ROUTES.CREATE_POST)}
              className="ml-auto bg-[#2d5f4d] hover:bg-[#234a3d] text-white px-6 py-2.5 rounded-lg text-[14px] font-medium transition-colors"
            >
              Создать пост
            </button>
          </div>
        </div>
      )}

      {/* Section Title */}
      <div className="mb-6">
        <h2 className="text-[24px] font-semibold text-gray-900">От велосипедистов</h2>
      </div>

      {/* Category Filters */}
      <div className="flex items-center gap-3 mb-6 flex-wrap">
        <button
          onClick={() => setSelectedCategory('all')}
          className={`px-5 py-2.5 rounded-xl text-[15px] font-medium transition-all ${
            selectedCategory === 'all'
              ? 'bg-[#2d5f4d] text-white'
              : 'bg-white text-gray-700 hover:bg-gray-50'
          }`}
        >
          Все записи
        </button>
        {POST_CATEGORIES.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-5 py-2.5 rounded-xl text-[15px] font-medium transition-all ${
              selectedCategory === category
                ? 'bg-[#2d5f4d] text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            {CATEGORY_LABELS[category]}
          </button>
        ))}
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 text-red-700 px-6 py-4 rounded-xl mb-6 text-[15px]">
          Не удалось загрузить публикации
        </div>
      )}

      {/* Posts List */}
      <div className="space-y-6">
        {filteredPosts.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl">
            <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5a2.5 2.5 0 00-2.5-2.5H15" />
            </svg>
            <p className="text-[18px] text-gray-500 mb-4">
              Пока нет публикаций
            </p>
            {isAuthenticated && (
              <button
                onClick={() => navigate(ROUTES.CREATE_POST)}
                className="bg-[#2d5f4d] hover:bg-[#234a3d] text-white px-6 py-3 rounded-lg text-[15px] font-medium transition-colors"
              >
                Создать первую публикацию
              </button>
            )}
          </div>
        ) : (
          filteredPosts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))
        )}
      </div>
    </div>
  );
};

export default FeedPage;
