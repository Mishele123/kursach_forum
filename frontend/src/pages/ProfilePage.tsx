import ProfilePosts from '../components/ProfilePosts';
import { Link } from 'react-router-dom';
import InlineUsername from '../components/InlineUsername';
import { useAuth } from '../context/AuthContext';
import { useBikes } from '../hooks';
import { bikesApi } from '../services/api';
import BikeImage from '../components/common/BikeImage';
import AvatarImage from '../components/common/AvatarImage';
import PhotoUpload from '../components/common/PhotoUpload';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const { bikes, isLoading, error, refetch } = useBikes();
  if (!user) return null;

  return <section className="velo-page profile-page simple-profile">
    <header className="page-heading">
      <div><h1>Мой профиль</h1></div>
    </header>

    <section className="velo-card profile-hero" aria-labelledby="profile-name">

      <div className="profile-hero-content">
        <div className="profile-identity">
          <div className="avatar large"><AvatarImage username={user.username} url={user.avatar_url} /></div>
          <div className="profile-identity-text">
            <InlineUsername />
            {(user.city || user.discipline) && <p className="profile-location">{[user.city, user.discipline].filter(Boolean).join(' · ')}</p>}
            <p className="profile-joined">С нами с <time dateTime={user.created_at}>{new Date(user.created_at).toLocaleDateString('ru-RU')}</time></p>
        {user.bio && <p className="post-text profile-bio">{user.bio}</p>}
        {user.interests.length > 0 ? <ul className="interest-tags profile-inline-interests" aria-label="Мои интересы">{user.interests.map((interest, index) => <li key={`${interest}-${index}`}>{interest}</li>)}</ul> : <Link className="profile-add-interests" to="/profile/edit">+ Добавить интересы</Link>}

          </div>
          <div className="profile-account-actions">
            <Link className="velo-button profile-edit" to="/profile/edit">Редактировать профиль</Link>
            <div className="profile-logout"><button type="button" onClick={logout}><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg><span>Выйти из аккаунта</span></button></div>
          </div>
        </div>
      </div>
    </section>
    <section className="velo-card profile-garage" aria-labelledby="profile-bikes-heading">
      <div className="profile-section-heading">
        <div><h2 id="profile-bikes-heading">Мои велосипеды{!isLoading && !error && <span className="profile-count">{bikes.length}</span>}</h2></div>
        <Link className="velo-button secondary" to="/bikes/add"><span aria-hidden="true">＋</span> Добавить велосипед</Link>
      </div>
      {isLoading ? <div className="velo-card" role="status">Загрузка велосипедов…</div>
        : error ? <div className="velo-card error" role="alert"><p>{error}</p><button type="button" className="velo-button secondary" onClick={refetch}>Повторить</button></div>
        : bikes.length ? <div className="profile-bikes-grid">{bikes.map(bike => <article className="velo-card profile-bike-card" key={bike.id}>
          <div className="profile-bike-media"><BikeImage bike={bike} /></div>
          <div className="profile-bike-content">
            <h3>{bike.brand} {bike.model}</h3><p>{bike.year} <span className="sr-only">· Год выпуска</span></p>
          </div>
            <details className="profile-bike-photo"><summary><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8" cy="8" r="1.5"/><path d="m3 17 6-6 4 4 3-3 5 5"/></svg><span>{bike.photo_url ? 'Изменить фото' : 'Добавить фото'}</span></summary>
              <PhotoUpload label="Сохранить фото" upload={async files => { await bikesApi.uploadPhoto(bike.id, files[0]); await refetch(); }} />
            </details>
        </article>)}</div>
        : <div className="velo-card profile-empty"><h3>У каждого велосипеда своя история</h3><p>Добавьте свой первый велосипед — познакомьтесь с владельцами похожих моделей.</p><Link className="velo-button secondary" to="/bikes/add">Добавить первый велосипед</Link></div>}
      <Link className="profile-garage-link" to="/bikes">Все велосипеды <span aria-hidden="true">→</span></Link>
    </section>
    <ProfilePosts key={user.id} userId={user.id} />

  </section>;
}
