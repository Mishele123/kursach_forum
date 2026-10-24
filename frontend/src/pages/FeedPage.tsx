import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { postsApi, errorMessage } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { POST_CATEGORIES, CATEGORY_LABELS } from '../utils/constants';
import PostCard from '../components/posts/PostCard';
import type { Post } from '../types';
const PAGE_SIZE = 10;
export default function FeedPage() {
  const [params, setParams] = useSearchParams();
  const category = params.get('category') || '';
  const q = params.get('q') || '';
  const { user } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [cursor, setCursor] = useState<string | undefined>();
  const [nextCursor,setNextCursor] = useState<string | null>(null);
  const [busy, setBusy] = useState(true);
  const [more, setMore] = useState(false);
  const [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let active = true; setBusy(true); setError('');
    void postsApi.getPosts(PAGE_SIZE,cursor).then(data => {
      if (!active) return;
      setPosts(old => cursor ? [...old,...data.items.filter(p=>!old.some(x=>x.id===p.id))] : data.items);
      setNextCursor(data.next_cursor); setMore(data.next_cursor!==null);
    }).catch(err => { if (active) setError(errorMessage(err)); }).finally(() => { if (active) setBusy(false); });
    return () => { active = false; };
  }, [cursor,retry]);
  const visiblePosts=posts.filter(p=>(!category || p.category===category) && (!q || (p.title+' '+p.text+' '+p.author.username).toLocaleLowerCase().includes(q.toLocaleLowerCase())));
  return <section className="velo-page feed-page"><h1>Ближе к людям. Дальше на велосипеде.</h1><p className="subtitle">Истории, опыт и новые открытия вашего сообщества</p>
    <div className="velo-card composer"><h2>Есть чем поделиться?</h2><Link className="composer-prompt" to={user ? '/post/create' : '/login'}>Маршрут, апгрейд или новая история...</Link><div><Link to="/post/create">+ Фото</Link><Link to="/post/create">Категория</Link><Link className="velo-button" to="/post/create">Создать пост</Link></div></div>
    <p className="subtitle">Поиск и категории применяются к загруженным публикациям. Загрузите ещё, чтобы увидеть больше.</p><div className="category-tabs"><button className={!category ? 'selected' : ''} onClick={() => setParams(q ? {q} : {})}>Все записи</button>{POST_CATEGORIES.map(c => <button key={c} className={category === c ? 'selected' : ''} onClick={() => setParams({category:c, ...(q ? {q} : {})})}>{CATEGORY_LABELS[c]}</button>)}</div>
    {q && <p>Поиск: {q} <button onClick={() => setParams(category ? {category} : {})}>Сбросить</button></p>}
    {error && <div className="error" role="alert">{error} <button onClick={() => setRetry(x => x+1)}>Повторить</button></div>}
    {visiblePosts.map(post => <PostCard key={post.id} post={post} />)}
    {busy && <p role="status">Загрузка публикаций...</p>}
    {!busy && !error && !visiblePosts.length && <div className="velo-card"><h2>Нет подходящих публикаций среди загруженных</h2><p>Поделитесь первой историей с сообществом.</p><Link className="velo-button" to="/post/create">Создать публикацию</Link></div>}
    {more && !error && <button className="velo-button secondary" disabled={busy} onClick={() => {if(nextCursor)setCursor(nextCursor);}}>Загрузить ещё</button>}
  </section>;
}
