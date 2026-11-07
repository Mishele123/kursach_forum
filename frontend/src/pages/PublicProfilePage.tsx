import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { peopleApi, errorMessage } from '../services/api';
import { useAuth } from '../context/AuthContext';
import AvatarImage from '../components/common/AvatarImage';
import BikeImage from '../components/common/BikeImage';
import PostCard from '../components/posts/PostCard';
import type { PublicProfile, Post } from '../types';
export default function PublicProfilePage() {
  const { id } = useParams();
  const { user } = useAuth();
  return <Profile key={id + String(user?.id)} id={Number(id)} />;
}
function Profile({ id }: { id: number }) {
  const [profile, setProfile] = useState<PublicProfile | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [cursor, setCursor] = useState<string>();
  const [next, setNext] = useState<string | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let active = true;
    setBusy(true); setError('');
    if (!Number.isInteger(id) || id < 1) { setError('Пользователь не найден'); setBusy(false); return; }
    void Promise.all([peopleApi.profile(id), peopleApi.posts(id, cursor)]).then(([person, page]) => {
      if (!active) return;
      setProfile(person);
      setPosts(old => cursor ? [...old, ...page.items.filter(post => !old.some(item => item.id === post.id))] : page.items);
      setNext(page.next_cursor);
    }).catch(err => { if (active) setError(errorMessage(err)); })
      .finally(() => { if (active) setBusy(false); });
    return () => { active = false; };
  }, [id, cursor, retry]);
  return <section className="velo-page profile-page simple-profile public-user-page">
    <Link className="back-link" to="/people">← Поиск людей</Link>
    <header className="page-heading"><h1>Профиль участника</h1></header>
    {profile && <>
      <section className="velo-card profile-hero" aria-labelledby="public-user-name"><div className="profile-hero-content"><div className="profile-identity">
        <div className="avatar large"><AvatarImage username={profile.username} url={profile.avatar_url} /></div>
        <div className="profile-identity-text"><h2 id="public-user-name">{profile.username}</h2><p className="profile-location">{[profile.city, profile.discipline].filter(Boolean).join(' · ') || 'Велосипедист сообщества'}</p>
          {profile.interests.length > 0 ? <ul className="interest-tags profile-inline-interests" aria-label="Интересы">{profile.interests.map((interest, index) => <li key={`${interest}-${index}`}>{interest}</li>)}</ul> : <p className="public-user-empty-interests">Интересы пока не указаны</p>}
        </div>
      </div></div></section>
      <section className="velo-card profile-garage" aria-labelledby="public-user-bikes"><div className="profile-section-heading"><h2 id="public-user-bikes">Велосипеды<span className="profile-count">{profile.bikes.length}</span></h2></div>
        {profile.bikes.length > 0 ? <div className="profile-bikes-grid">{profile.bikes.map(bike => <article className="velo-card profile-bike-card" key={bike.id}><div className="profile-bike-media"><BikeImage bike={bike} /></div><div className="profile-bike-content"><h3>{bike.brand} {bike.model}</h3><p>{bike.year}</p></div></article>)}</div> : <div className="profile-empty"><p>Велосипеды пока не добавлены.</p></div>}
      </section>
      <section className="profile-publications" aria-labelledby="public-user-posts"><div className="profile-section-heading"><h2 id="public-user-posts">Публикации</h2></div>
        {posts.map(post => <PostCard key={post.id} post={post} compact />)}
        {!posts.length && !busy && !error && <div className="velo-card profile-empty"><p>Публикаций пока нет.</p></div>}
      </section>
    </>}
    {error && <div className="error" role="alert"><p>{error}</p><button type="button" className="velo-button secondary" onClick={() => setRetry(value => value + 1)}>Повторить</button></div>}
    {busy && <p role="status">Загрузка профиля…</p>}
    {next && !error && <button type="button" className="velo-button secondary" disabled={busy} onClick={() => { if (next) { setBusy(true); setCursor(next); } }}>Загрузить ещё публикации</button>}
  </section>;
}
