import { Link, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { bikesApi } from '../../services/api';
import type { Bike } from '../../types';
import Landscape from '../common/Landscape';
import BikeImage from '../common/BikeImage';
export default function RightSidebar() {
  const { user } = useAuth();
  const { pathname } = useLocation();
  const [bike, setBike] = useState<Bike | null>(null);
  useEffect(() => { let active = true; setBike(null); if (user && pathname !== '/profile' && pathname !== '/bikes') void bikesApi.getMyBikes().then(b => { if (active) setBike(b[0] || null); }).catch(() => {}); return () => { active = false; }; }, [user, pathname]);
  if (pathname === '/bikes') return <aside className="velo-right garage-aside" aria-label="Ваш гараж">
    <section className="velo-card"><svg className="garage-aside-icon" width="44" height="32" viewBox="0 0 96 64" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="22" cy="43" r="16"/><circle cx="75" cy="43" r="16"/><path d="m22 43 18-29 14 29H22l15-23h27l11 23M54 43 67 8h-9M33 12h14"/></svg><h2>Ваш гараж</h2><p>Добавьте фотографии, чтобы узнавать свои велосипеды с первого взгляда.</p><Link className="velo-button secondary" to="/profile">Мой профиль</Link></section>
    <section className="velo-card"><svg className="garage-aside-icon" width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 4a3 3 0 0 1 0 6M22 21v-3a6 6 0 0 0-5-6"/></svg><h2>Найдите своих людей</h2><p>Познакомьтесь с владельцами похожих велосипедов.</p><Link className="velo-button garage-people-link" to="/people">Поиск людей</Link></section>
    <small>VELO © 2026<br/>Сообщество. Опыт. Движение.</small>
  </aside>;
  if (pathname === '/profile' && user) {
    const fields = [
      { label: 'Фото профиля', done: !!user.avatar_url },
      { label: 'Город', done: !!user.city },
      { label: 'Дисциплина', done: !!user.discipline },
      { label: 'Интересы', done: user.interests.length > 0 },
    ];
    const complete = fields.every(field => field.done);
    return <aside className="velo-right profile-aside" aria-label="Ваш профиль">
      <section className="velo-card"><p className="eyebrow">ВАШ ПРОФИЛЬ</p><h2>{complete ? 'Приятно познакомиться!' : 'Расскажите о себе'}</h2>
        <p>{complete ? 'Основная информация заполнена. Найдите людей, которые разделяют ваши интересы.' : 'Помогите другим велосипедистам узнать вас и найти общие интересы.'}</p>
        <ul className="profile-checklist">{fields.map(field => <li key={field.label} className={field.done ? 'complete' : ''}><span aria-hidden="true">{field.done ? '✓' : '○'}</span>{field.label}<span className="sr-only">{field.done ? ': заполнено' : ': не заполнено'}</span></li>)}</ul>
        <Link className="velo-button secondary" to={'/profile/edit'}>{complete ? 'Редактировать профиль' : 'Заполнить профиль'}</Link>
      </section>
      <section className="velo-card profile-community-card">
        <svg className="profile-community-icon" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3zM16 4a3 3 0 0 1 0 6M19 21h3v-3a6 6 0 0 0-5-6"/></svg>
        <h2>Вместе интереснее</h2><p>Найдите велосипедистов с похожими интересами.</p>
        <Link className="velo-button profile-find-people" to="/people">Найти людей</Link>
      </section>
      <small>VELO © 2026<br/>Сообщество. Опыт. Движение.</small>
    </aside>;
  }
  return <aside className="velo-right"><div className="garage-card"><p className="eyebrow">{bike ? 'МОЙ ВЕЛОСИПЕД' : 'ВАШ СЛЕДУЮЩИЙ ВЫЕЗД'}</p><h2>{bike ? `${bike.brand} ${bike.model}` : 'Всё начинается с велосипеда.'}</h2>{bike ? <BikeImage bike={bike} /> : <Landscape />}{bike && <p>{bike.year} · Год выпуска</p>}<Link className="velo-button secondary" to="/bikes">Мой гараж</Link></div>
    <div className="velo-card"><h2>{pathname === '/people' ? 'Вместе интереснее' : user ? `Добро пожаловать, ${user.username}!` : 'Вместе интереснее!'}</h2><p>{pathname === '/people' ? 'Заполните город и интересы, чтобы другим было проще вас найти.' : 'Расскажите о себе и своих интересах — так вас быстрее найдут единомышленники.'}</p><Link className="velo-button secondary" to={user ? '/profile/edit' : '/register'}>{user ? 'Заполнить профиль' : 'Присоединиться'}</Link></div>
    <small>VELO © 2026<br/>Сообщество. Опыт. Движение.</small></aside>;
}
