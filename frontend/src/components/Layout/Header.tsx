import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AvatarImage from '../common/AvatarImage';
export default function Header() {
  const { user } = useAuth();
  const navigate = useNavigate();
  return <header className="velo-header">
    <Link className="logo" to="/feed">velo.</Link>
    <form className="header-search" onSubmit={e => { e.preventDefault(); const data = new FormData(e.currentTarget); navigate('/feed?q=' + encodeURIComponent(String(data.get('q') || ''))); }}><input name="q" aria-label="Поиск историй" placeholder="Поиск людей, велосипедов и историй" /></form>
    <span className="header-tagline">Сообщество велосипедистов</span>
    <Link className="velo-button" to={user ? '/post/create' : '/login'}>{user ? '+ Создать пост' : 'Войти'}</Link>
    {user && <Link className="avatar" aria-label="Мой профиль" to="/profile"><AvatarImage username={user.username} url={user.avatar_url} /></Link>}
  </header>;
}
