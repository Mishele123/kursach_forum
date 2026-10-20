import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { ROUTES } from '../../utils/constants';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  const navItems = [
    {
      label: 'Лента',
      path: ROUTES.FEED,
    },
    {
      label: 'Мой профиль',
      path: ROUTES.PROFILE,
      protected: true,
    },
    {
      label: 'Мои велосипеды',
      path: ROUTES.MY_BIKES,
      protected: true,
    },
    {
      label: 'Сохранённое',
      path: ROUTES.SAVED,
      protected: true,
    },
  ];

  const categoryItems = [
    { label: 'Маршруты', count: 124 },
    { label: 'Обслуживание', count: 89 },
    { label: 'Апгрейд', count: 67 },
    { label: 'Трюки', count: 43 },
  ];

  return (
    <aside className="w-[224px] bg-white min-h-[calc(100vh-72px)] sticky top-[72px] overflow-y-auto flex flex-col">
      <div className="p-6 flex-1">
        {/* Main Navigation */}
        <div className="mb-8">
          <h3 className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-3">
            ВАШЕ ПРОСТРАНСТВО
          </h3>
          <nav className="space-y-1">
            {navItems.map((item) => {
              if (item.protected && !isAuthenticated) return null;

              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`block px-4 py-3 rounded-lg text-[15px] font-normal transition-colors ${
                    isActive
                      ? 'bg-[#2d5f4d] text-white'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Categories */}
        <div className="mb-8">
          <h3 className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-3">
            ТЕМЫ ДЛЯ ВДОХНОВЕНИЯ
          </h3>
          <div className="space-y-1">
            {categoryItems.map((category) => (
              <button
                key={category.label}
                className="w-full flex items-center justify-between px-4 py-2.5 rounded-lg text-[15px] text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <span>{category.label}</span>
                <span className="text-sm text-gray-400">{category.count}</span>
              </button>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-[#f5f3f0] rounded-xl p-5 mt-auto">
          <h4 className="font-semibold text-[#2d5f4d] text-[15px] mb-2 leading-tight">
            Всё начинается<br />с велосипеда.
          </h4>
          <p className="text-[13px] text-gray-600 mb-4 leading-relaxed">
            Добавьте свой байк и найдите владельцев похожих моделей.
          </p>
          <Link
            to={ROUTES.ADD_BIKE}
            className="block w-full bg-[#2d5f4d] hover:bg-[#234a3d] text-white text-center py-2.5 rounded-lg text-[13px] font-medium transition-colors"
          >
            Добавить велосипед
          </Link>
        </div>
      </div>

      {/* Footer */}
      <div className="p-6 pt-0 mt-auto">
        <div className="text-[11px] text-gray-400 space-y-0.5">
          <div>VELO © 2026</div>
          <div>Сообщество Опыт. Движение.</div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
