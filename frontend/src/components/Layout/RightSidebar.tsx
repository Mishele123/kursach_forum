import { Link, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { bikesApi } from '../../services/api';
import type { Bike } from '../../types';
import Landscape from '../common/Landscape';
export default function RightSidebar() {
  const { user } = useAuth();
  const { pathname } = useLocation();
  const [bike, setBike] = useState<Bike | null>(null);
  useEffect(() => { let active = true; setBike(null); if (user) void bikesApi.getMyBikes().then(b => { if (active) setBike(b[0] || null); }).catch(() => {}); return () => { active = false; }; }, [user, pathname]);
  return <aside className="velo-right"><div className="garage-card"><p className="eyebrow">{bike ? 'МОЙ ВЕЛОСИПЕД' : 'ВАШ СЛЕДУЮЩИЙ ВЫЕЗД'}</p><h2>{bike ? `${bike.brand} ${bike.model}` : 'Всё начинается с велосипеда.'}</h2><Landscape />{bike && <p>{bike.year} · Год выпуска</p>}<Link className="velo-button secondary" to="/bikes">Мой гараж</Link></div>
    <div className="velo-card"><h2>{user ? `Добро пожаловать, ${user.username}!` : 'Вместе интереснее!'}</h2><p>Расскажите о себе и своих интересах — так вас быстрее найдут единомышленники.</p><Link className="velo-button secondary" to={user ? '/profile/edit' : '/register'}>{user ? 'Заполнить профиль' : 'Присоединиться'}</Link></div>
    <small>VELO © 2026<br/>Сообщество. Опыт. Движение.</small></aside>;
}
