import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { errorMessage } from '../services/api';
import { Input } from '../components/common';
import Landscape from '../components/common/Landscape';
export default function AuthPage({ registration = false }: { registration?: boolean }) {
 const { login, register } = useAuth(); const navigate = useNavigate();
 const [busy,setBusy] = useState(false); const [error,setError] = useState('');
 async function submit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault(); setError(''); const data=new FormData(event.currentTarget);
  const email=String(data.get('email')).trim(); const password=String(data.get('password'));
  if(registration && password !== data.get('confirm')) { setError('Пароли не совпадают'); return; }
  setBusy(true);
  try { if(registration) await register({username:String(data.get('username')).trim(),email,password}); else await login({username:email,password}); navigate('/feed'); }
  catch(err) { setError(errorMessage(err)); } finally {setBusy(false);}
 }
 return <main className="auth-screen"><section className="auth-hero"><Link className="logo" to="/feed">velo.</Link><h1>Больше, чем просто велосипед.</h1><p>Люди, маршруты и опыт, которые делают каждую поездку лучше.</p><Landscape/><p>Сообщество велосипедистов</p></section>
 <section className="auth-form"><h1>{registration ? 'Создать аккаунт' : 'С возвращением!'}</h1><p className="subtitle">{registration ? 'Присоединяйтесь к сообществу велосипедистов' : 'Войдите, чтобы поделиться своей историей'}</p>
 <form onSubmit={submit}>{error && <p className="error" role="alert">{error}</p>}
 {registration && <Input label="Имя пользователя" name="username" required minLength={3} maxLength={50} autoComplete="username" disabled={busy}/>}
 <Input label="Email" type="email" name="email" required maxLength={254} autoComplete="email" placeholder="minh@example.com" disabled={busy}/>
 <Input label="Пароль" type="password" name="password" required minLength={registration ? 6 : 1} maxLength={256} autoComplete={registration ? 'new-password' : 'current-password'} disabled={busy}/>
 {registration && <Input label="Подтвердите пароль" type="password" name="confirm" required autoComplete="new-password" disabled={busy}/>}
 <button className="velo-button" type="submit" disabled={busy}>{busy ? 'Подождите...' : registration ? 'Создать аккаунт' : 'Войти'}</button></form>
 <hr/><p className="subtitle">{registration ? 'Уже есть аккаунт?' : 'Впервые здесь?'}</p><Link className="velo-button secondary" to={registration ? '/login' : '/register'}>{registration ? 'Войти' : 'Создать аккаунт'}</Link><Link className="velo-button secondary" to="/feed">Посмотреть ленту</Link></section></main>;
}
