import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useBikes } from '../hooks';
import api, { errorMessage } from '../services/api';
import type { Post } from '../types';
import PostCard from '../components/posts/PostCard';
export default function ProfilePage() {
  const { user, logout } = useAuth();
  const { bikes, isLoading, error } = useBikes();
  const [posts, setPosts] = useState<Post[]>([]);
  const [postError, setPostError] = useState('');
  const [more, setMore] = useState(false);
  const [busy, setBusy] = useState(false);
  const [page, setPage] = useState(0);
  useEffect(() => { if (!user) return; let active=true; setBusy(true); void api.get<Post[]>('/posts',{params:{author_id:user.id,limit:11,offset:page*10}}).then(({data}) => { if(active) { setPosts(old => page ? [...old,...data.slice(0,10)] : data.slice(0,10)); setMore(data.length>10); } }).catch(e => {if(active) setPostError(errorMessage(e));}).finally(() => {if(active) setBusy(false);}); return () => {active=false;}; },[user,page]);
  if (!user) return null;
  return <section className="velo-page"><h1>Мой профиль</h1><p className="subtitle">Ваши истории, интересы и велосипеды в одном месте</p>
    <div className="velo-card"><div className="avatar large">{user.username.slice(0,2).toUpperCase()}</div><h2>{user.username}</h2><p>{[user.city,user.discipline].filter(Boolean).join(' · ') || 'Расскажите о своих увлечениях'}</p><p className="post-text">{user.bio}</p><p>С нами с {new Date(user.created_at).toLocaleDateString('ru-RU')}</p><div className="form-actions"><Link className="velo-button" to="/profile/edit">Редактировать профиль</Link><button className="velo-button secondary" onClick={logout}>Выйти из аккаунта</button></div></div>
    <h2>Мои велосипеды</h2><div className="velo-card">{isLoading ? <p>Загрузка...</p> : error ? <p role="alert">{error}</p> : bikes.length ? bikes.map(b => <p key={b.id}><strong>{b.brand} {b.model}</strong> · {b.year}</p>) : <p>У вас пока нет велосипедов</p>}<Link to="/bikes" className="velo-button secondary">Открыть гараж</Link></div>
    <h2>Мои интересы</h2><div className="velo-card"><p>{user.interests || 'Добавьте интересы в настройках профиля.'}</p></div>
    <h2>Мои публикации</h2>{postError && <p role="alert">{postError}</p>}{posts.map(p => <PostCard key={p.id} post={p}/>)}{busy && <p role="status">Загрузка...</p>}{!busy && !posts.length && !postError && <div className="velo-card"><p>Здесь появятся ваши публикации.</p><Link to="/post/create">Поделиться историей →</Link></div>}{more && <button className="velo-button secondary" disabled={busy} onClick={() => setPage(p=>p+1)}>Загрузить ещё</button>}
  </section>;
}
