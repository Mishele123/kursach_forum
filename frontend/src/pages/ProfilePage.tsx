import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useBikes } from '../hooks';
import AvatarImage from '../components/common/AvatarImage';
export default function ProfilePage() {
 const {user,logout}=useAuth(); const {bikes,isLoading,error}=useBikes(); if(!user)return null;
 return <section className="velo-page"><h1>Мой профиль</h1><div className="velo-card"><div className="avatar large"><AvatarImage username={user.username}/></div><h2>{user.username}</h2><p>{[user.city,user.discipline].filter(Boolean).join(' · ')}</p><p className="post-text">{user.bio}</p><p>С нами с {new Date(user.created_at).toLocaleDateString('ru-RU')}</p><div className="form-actions"><Link className="velo-button" to="/profile/edit">Редактировать профиль</Link><button className="velo-button secondary" onClick={logout}>Выйти из аккаунта</button></div></div>
 <h2>Мои интересы</h2><div className="velo-card">{user.interests.join(', ')||'Добавьте интересы в настройках профиля.'}</div>
 <h2>Мои велосипеды</h2><div className="velo-card">{isLoading?<p>Загрузка...</p>:error?<p role="alert">{error}</p>:bikes.length?bikes.map(b=><p key={b.id}><strong>{b.brand} {b.model}</strong> · {b.year}</p>):<p>У вас пока нет велосипедов</p>}<Link to="/bikes" className="velo-button secondary">Открыть гараж</Link></div></section>;
}
