import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../../api/api';

export default function Header({ user, onLogout }) {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            await authAPI.logout();
            onLogout();
            navigate('/login');
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    return (
        <header className="site-header">
            <div className="container">
                <h1 className="site-title">Велосипедное Сообщество</h1>
                <nav className="main-nav">
                    {user ? (
                        <>
                            <Link to="/" className="nav-link">Лента</Link>
                            <Link to="/profile" className="nav-link">Профиль</Link>
                            <button onClick={handleLogout} className="nav-link">Выход</button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="nav-link">Вход</Link>
                            <Link to="/register" className="nav-link">Регистрация</Link>
                        </>
                    )}
                </nav>
            </div>
        </header>
    );
}
