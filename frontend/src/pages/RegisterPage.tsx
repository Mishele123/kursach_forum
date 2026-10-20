import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Input } from '../components/common';
import { ROUTES, MIN_USERNAME_LENGTH, MIN_PASSWORD_LENGTH } from '../utils/constants';

const RegisterPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!username || !password || !confirmPassword) {
      setError('Пожалуйста, заполните все поля');
      return;
    }

    if (username.length < MIN_USERNAME_LENGTH) {
      setError(`Имя пользователя должно содержать минимум ${MIN_USERNAME_LENGTH} символа`);
      return;
    }

    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(`Пароль должен содержать минимум ${MIN_PASSWORD_LENGTH} символов`);
      return;
    }

    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    setIsLoading(true);

    try {
      await register({ username, password });
      navigate(ROUTES.FEED);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка регистрации. Возможно, это имя пользователя уже занято.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Hero */}
      <div className="hidden lg:flex lg:w-1/2 bg-velo-green relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-velo-green to-velo-green-700"></div>
        <div className="relative z-10 flex flex-col justify-center px-16 text-white">
          <h1 className="text-5xl font-bold mb-6">
            Больше, чем просто велосипед.
          </h1>
          <p className="text-xl text-velo-green-50 mb-8 max-w-md leading-relaxed">
            Люди, маршруты и опыт, которые делают каждую поездку лучше.
          </p>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-velo-green-400 rounded-2xl flex items-center justify-center">
              <svg className="w-10 h-10" fill="currentColor" viewBox="0 0 24 24">
                <path d="M5 18c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm14.8-11.4c-.3-.3-.7-.4-1.1-.4h-2.4l-2.3-4H10v2h3l2.4 4.2-4.4 7.8H5c-.6 0-1 .4-1 1s.4 1 1 1h1.8c-.3.5-.5 1.1-.5 1.8 0 1.7 1.3 3 3 3s3-1.3 3-3c0-.7-.2-1.3-.5-1.8h5.3c-.3.5-.5 1.1-.5 1.8 0 1.7 1.3 3 3 3s3-1.3 3-3c0-1.1-.6-2-1.4-2.5L18.8 7z" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-velo-green-100">Сообщество велосипедистов</p>
              <p className="text-xs text-velo-green-200">velo.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Register Form */}
      <div className="flex-1 flex items-center justify-center px-6 bg-white">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Создать аккаунт
            </h2>
            <p className="text-gray-600">
              Присоединяйтесь к сообществу велосипедистов
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <Input
              label="Имя пользователя"
              type="text"
              placeholder="minh_chan"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading}
            />

            <Input
              label="Пароль"
              type="password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />

            <Input
              label="Подтвердите пароль"
              type="password"
              placeholder="••••••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={isLoading}
            />

            <Button
              type="submit"
              variant="primary"
              fullWidth
              isLoading={isLoading}
            >
              Создать аккаунт
            </Button>
          </form>

          <div className="mt-6 text-center space-y-4">
            <p className="text-sm text-gray-600">
              Уже есть аккаунт?{' '}
              <Link
                to={ROUTES.LOGIN}
                className="text-velo-green hover:text-velo-green-600 font-semibold"
              >
                Войти
              </Link>
            </p>

            <Link
              to={ROUTES.FEED}
              className="block text-sm text-gray-500 hover:text-velo-green transition-colors"
            >
              Посмотреть ленту
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
