import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { authAPI } from './api/api';
import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';
import LoginForm from './components/Auth/LoginForm';
import RegisterForm from './components/Auth/RegisterForm';
import FeedPage from './components/Feed/FeedPage';
import ProfilePage from './components/Profile/ProfilePage';

function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const currentUser = await authAPI.getCurrentUser();
            setUser(currentUser);
        } catch (error) {
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const handleLogin = (userData) => {
        setUser(userData);
    };

    const handleLogout = () => {
        setUser(null);
    };

    if (loading) {
        return <div className="loading">Загрузка...</div>;
    }

    return (
        <Router>
            <Header user={user} onLogout={handleLogout} />
            <main style={{ flex: 1 }}>
                <Routes>
                    <Route
                        path="/"
                        element={user ? <FeedPage /> : <Navigate to="/login" />}
                    />
                    <Route
                        path="/login"
                        element={!user ? <LoginForm onLogin={handleLogin} /> : <Navigate to="/" />}
                    />
                    <Route
                        path="/register"
                        element={!user ? <RegisterForm /> : <Navigate to="/" />}
                    />
                    <Route
                        path="/profile"
                        element={user ? <ProfilePage user={user} /> : <Navigate to="/login" />}
                    />
                </Routes>
            </main>
            <Footer />
        </Router>
    );
}

export default App;
