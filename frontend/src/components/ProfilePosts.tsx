import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { peopleApi, errorMessage } from '../services/api';
import type { Post } from '../types';
import PostCard from './posts/PostCard';

export default function ProfilePosts({ userId }: { userId: number }) {
  const [posts, setPosts] = useState<Post[]>([]);
  const [cursor, setCursor] = useState<string>();
  const [next, setNext] = useState<string | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let active = true;
    setBusy(true); setError('');
    void peopleApi.posts(userId, cursor).then(page => {
      if (!active) return;
      setPosts(old => cursor ? [...old, ...page.items.filter(post => !old.some(item => item.id === post.id))] : page.items);
      setNext(page.next_cursor);
    }).catch(err => { if (active) setError(errorMessage(err)); })
      .finally(() => { if (active) setBusy(false); });
    return () => { active = false; };
  }, [userId, cursor, retry]);
  return <section className="profile-publications" aria-labelledby="my-publications-heading">
    <div className="profile-section-heading"><h2 id="my-publications-heading">Мои публикации</h2><Link to="/post/create">+ Создать пост</Link></div>
    {posts.map(post => <PostCard key={post.id} post={post} compact />)}
    {busy && <p role="status">Загрузка публикаций…</p>}
    {error && <div className="error" role="alert"><p>{error}</p><button type="button" className="velo-button secondary" onClick={() => setRetry(value => value + 1)}>Повторить</button></div>}
    {!posts.length && !busy && !error && <div className="velo-card profile-empty"><h3>Здесь начинается ваша история</h3><p>Вы ещё не опубликовали ни одного поста. Поделитесь первым маршрутом или историей о велосипеде.</p><Link className="velo-button secondary" to="/post/create">Создать первый пост</Link></div>}
    {next && !error && <button type="button" className="velo-button secondary" disabled={busy} onClick={() => { if (next) { setBusy(true); setCursor(next); } }}>Загрузить ещё публикации</button>}
  </section>;
}

