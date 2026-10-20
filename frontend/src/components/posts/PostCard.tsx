import React from 'react';
import { Link } from 'react-router-dom';
import { getUserInitials, formatRelativeTime } from '../../utils/helpers';
import type { Post } from '../../types';

interface PostCardProps {
  post: Post;
}

const PostCard: React.FC<PostCardProps> = ({ post }) => {
  // Mock data for demonstration
  const mockBikeDetails = {
    bike: 'Trek Marlin 7',
    mtb: 'MTB',
    terrain: 'Гравий / лес',
    distance: '42 км',
    elevation: '380 м'
  };

  return (
    <div className="bg-white rounded-2xl overflow-hidden">
      <div className="p-6">
        {/* Header: Author info */}
        <div className="flex items-start gap-3 mb-4">
          {/* Avatar */}
          <div className="w-10 h-10 bg-[#d4e4d9] rounded-full flex items-center justify-center font-semibold text-[#2d5f4d] text-[14px] flex-shrink-0">
            {post.author_username ? getUserInitials(post.author_username) : 'АК'}
          </div>

          {/* Author name, bike, time */}
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-gray-900 text-[15px]">
              {post.author_username || 'Алексей Козлов'}
            </div>
            <div className="text-[13px] text-gray-500">
              {mockBikeDetails.bike} · {mockBikeDetails.mtb} · Самара · {formatRelativeTime(post.created_at)}
            </div>
          </div>
        </div>

        {/* Category Badge */}
        <div className="mb-3">
          <span className="inline-flex items-center px-3 py-1.5 rounded-md text-[13px] font-medium bg-[#d4e4d9] text-[#2d5f4d]">
            Маршруты
          </span>
        </div>

        {/* Title */}
        <Link to={`/post/${post.id}`}>
          <h3 className="text-[22px] font-bold text-gray-900 mb-3 hover:text-[#2d5f4d] transition-colors leading-tight">
            {post.title}
          </h3>
        </Link>

        {/* Excerpt */}
        <p className="text-[15px] text-gray-600 mb-4 leading-relaxed line-clamp-2">
          {post.text}
        </p>
      </div>

      {/* Image */}
      {post.photo_url && (
        <div className="relative">
          <img 
            src={post.photo_url} 
            alt={post.title}
            className="w-full h-[400px] object-cover"
            loading="lazy"
          />
        </div>
      )}

      {/* Stats Bar */}
      <div className="px-6 py-4 bg-[#f5f3f0] flex items-center gap-6 text-[14px] text-gray-700">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          <span className="font-medium">{mockBikeDetails.distance}</span>
        </div>

        <div className="flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          <span className="font-medium">{mockBikeDetails.elevation}</span>
        </div>

        <div className="flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
          </svg>
          <span className="font-medium">{mockBikeDetails.terrain}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="px-6 py-4 flex items-center gap-6 text-[14px] text-gray-600 border-t border-gray-100">
        <button className="flex items-center gap-2 hover:text-[#2d5f4d] transition-colors">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <span>128</span>
        </button>

        <button className="flex items-center gap-2 hover:text-[#2d5f4d] transition-colors">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <span>Обсудить · 24</span>
        </button>

        <button className="flex items-center gap-2 hover:text-[#2d5f4d] transition-colors ml-auto">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          <span>Сохранить</span>
        </button>
      </div>
    </div>
  );
};

export default PostCard;
