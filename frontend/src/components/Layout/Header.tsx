import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { ROUTES } from '../../utils/constants';
import { getUserInitials } from '../../utils/helpers';

const Header: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-[1440px] mx-auto px-8 h-[72px] flex items-center justify-between">
        {/* Logo */}
        <Link to={ROUTES.FEED} className="flex items-center">
          <span className="text-[24px] font-semibold text-[#2d5f4d]">velo.</span>
        </Link>

        {/* Search Bar */}
        <div className="flex-1 max-w-[420px] mx-8">
          <input
            type="text"
            placeholder="Поиск людей, велосипедов и историй"
            className="w-full px-4 py-2.5 bg-[#f5f3f0] rounded-lg text-sm text-gray-700 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#2d5f4d]"
          />
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-6">
          <span className="text-sm text-gray-600">
            Сообщество велосипедистов
          </span>
          
          {isAuthenticated ? (
            <>
              <button
                onClick={() => navigate(ROUTES.CREATE_POST)}
                className="bg-[#2d5f4d] hover:bg-[#234a3d] text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors"
              >
                + Создать пост
              </button>
              <button
                onClick={() => navigate(ROUTES.PROFILE)}
                className="w-10 h-10 bg-[#2d5f4d] text-white rounded-full flex items-center justify-center font-medium text-sm transition-colors hover:bg-[#234a3d]"
              >
                {user ? getUserInitials(user.username) : 'МТ'}
              </button>
            </>
          ) : (
            <Link
              to={ROUTES.LOGIN}
              className="bg-[#2d5f4d] hover:bg-[#234a3d] text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-colors"
            >
              Войти
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
