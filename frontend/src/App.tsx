import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { MainLayout } from './components/layout';
import { ProtectedRoute } from './components/auth';
import { ROUTES } from './utils/constants';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import FeedPage from './pages/FeedPage';
import CreatePostPage from './pages/CreatePostPage';
import ProfilePage from './pages/ProfilePage';

// Import styles
import './styles/tailwind.css';
import './index.css';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes (No Layout) */}
          <Route path={ROUTES.LOGIN} element={<LoginPage />} />
          <Route path={ROUTES.REGISTER} element={<RegisterPage />} />

          {/* Routes with Layout */}
          <Route element={<MainLayout />}>
            {/* Public Feed */}
            <Route path={ROUTES.FEED} element={<FeedPage />} />
            <Route path={ROUTES.HOME} element={<Navigate to={ROUTES.FEED} replace />} />

            {/* Protected Routes */}
            <Route
              path={ROUTES.CREATE_POST}
              element={
                <ProtectedRoute>
                  <CreatePostPage />
                </ProtectedRoute>
              }
            />
            <Route
              path={ROUTES.PROFILE}
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            
            {/* Placeholder for other protected routes */}
            <Route
              path={ROUTES.MY_BIKES}
              element={
                <ProtectedRoute>
                  <div className="py-8 px-6">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Мои велосипеды</h1>
                    <p className="text-gray-600">Страница в разработке...</p>
                  </div>
                </ProtectedRoute>
              }
            />
            <Route
              path={ROUTES.SAVED}
              element={
                <ProtectedRoute>
                  <div className="py-8 px-6">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Сохранённое</h1>
                    <p className="text-gray-600">Страница в разработке...</p>
                  </div>
                </ProtectedRoute>
              }
            />
          </Route>

          {/* 404 */}
          <Route
            path="*"
            element={
              <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                  <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
                  <p className="text-xl text-gray-600 mb-8">Страница не найдена</p>
                  <a
                    href={ROUTES.FEED}
                    className="bg-velo-green hover:bg-velo-green-600 text-white px-6 py-3 rounded-xl font-semibold transition-colors inline-block"
                  >
                    Вернуться на главную
                  </a>
                </div>
              </div>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
