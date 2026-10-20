import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useBikes } from '../hooks';
import { Button, Card, Loading } from '../components/common';
import { getUserInitials } from '../utils/helpers';
import { ROUTES } from '../utils/constants';

const ProfilePage: React.FC = () => {
  const { user, logout } = useAuth();
  const { bikes, isLoading: bikesLoading } = useBikes();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate(ROUTES.LOGIN);
  };

  if (!user) {
    return <Loading message="Загрузка профиля..." />;
  }

  return (
    <div className="py-8 px-6">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Мой профиль
        </h1>
        <p className="text-gray-600">
          Ваши истории, интересы и велосипеды в одном месте
        </p>
      </div>

      {/* Profile Card */}
      <Card className="mb-6">
        <div className="flex items-start gap-6">
          {/* Avatar */}
          <div className="flex-shrink-0">
            <div className="w-24 h-24 bg-velo-green rounded-2xl flex items-center justify-center text-white font-bold text-3xl shadow-lg">
              {getUserInitials(user.username)}
            </div>
          </div>

          {/* Info */}
          <div className="flex-1">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              {user.username}
            </h2>
            <p className="text-gray-600 mb-4">
              {user.city || 'Самара'} · {user.discipline || 'MTB'} · {user.interests || 'Люблю лесные маршруты'}
            </p>
            {user.bio && (
              <p className="text-gray-700 mb-4 leading-relaxed">
                {user.bio}
              </p>
            )}

            {/* Stats */}
            <div className="flex items-center gap-6 mb-4">
              <div>
                <span className="block text-2xl font-bold text-gray-900">12</span>
                <span className="text-sm text-gray-500">публикаций</span>
              </div>
              <div>
                <span className="block text-2xl font-bold text-gray-900">{bikes.length}</span>
                <span className="text-sm text-gray-500">велосипед</span>
              </div>
              <div>
                <span className="block text-2xl font-bold text-gray-900">С нами с 2026</span>
                <span className="text-sm text-gray-500"></span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">
              <Link to={ROUTES.EDIT_PROFILE}>
                <Button variant="primary">
                  Редактировать профиль
                </Button>
              </Link>
              <Button variant="secondary" onClick={handleLogout}>
                Выйти из аккаунта
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {/* Bikes Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Мой велосипед</h2>
          <Link to={ROUTES.MY_BIKES}>
            <Button variant="outline" className="text-sm">
              Открыть гараж
            </Button>
          </Link>
        </div>

        {bikesLoading ? (
          <Loading message="Загрузка велосипедов..." />
        ) : bikes.length === 0 ? (
          <Card>
            <div className="text-center py-8">
              <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <p className="text-gray-600 mb-4">У вас пока нет велосипедов</p>
              <Link to={ROUTES.ADD_BIKE}>
                <Button variant="primary">
                  Добавить велосипед
                </Button>
              </Link>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {bikes.slice(0, 2).map((bike) => (
              <Card key={bike.id} className="border-l-4 border-velo-green">
                <h3 className="text-xl font-bold text-gray-900 mb-1">
                  {bike.brand} {bike.model}
                </h3>
                <p className="text-gray-600 mb-3">
                  {bike.year} · Горный велосипед · 29"
                </p>
                <button className="text-velo-green hover:text-velo-green-600 font-semibold text-sm">
                  Мой гараж →
                </button>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Interests Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Мои интересы</h2>
        <Card>
          <div className="flex flex-wrap gap-2">
            {['MTB', 'Маршруты', 'Апгрейд', 'Велопутешествия'].map((interest) => (
              <span
                key={interest}
                className="px-4 py-2 bg-velo-green-50 text-velo-green rounded-lg font-semibold text-sm"
              >
                {interest}
              </span>
            ))}
          </div>
        </Card>
      </div>

      {/* Publications */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Мои публикации</h2>
        <Card>
          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">Здесь появятся ваши публикации</p>
            <Link to={ROUTES.CREATE_POST}>
              <Button variant="primary">
                Первый выезд на Trek Marlin 7
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ProfilePage;
