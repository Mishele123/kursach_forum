import { useState } from 'react';
import type { FormEvent } from 'react';
import { isAxiosError } from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { errorMessage } from '../services/api';
import { Input } from '../components/common';
export default function AuthPage({ registration = false }: { registration?: boolean }) {
 const { login, register } = useAuth(); const navigate = useNavigate();
 const [busy,setBusy] = useState(false); const [error,setError] = useState('');
 const [passwordError, setPasswordError] = useState('');
 const invalidCredentials = 'Неверный email или пароль.';
 async function submit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault(); setError(''); setPasswordError(''); const data=new FormData(event.currentTarget);
  const email=String(data.get('email')).trim(); const password=String(data.get('password'));
  if (!registration && password.length < 8) {
   setPasswordError(invalidCredentials);
   return;
  }
  if(registration && password !== data.get('confirm')) { setError('Пароли не совпадают'); return; }
  setBusy(true);
  try { if(registration) await register({username:String(data.get('username')).trim(),email,password}); else await login({email,password,remember_me:data.get('remember')==='on'}); navigate('/feed'); }
  catch(err) {
   if (!registration && isAxiosError(err) && err.response?.status === 401) setPasswordError(invalidCredentials);
   else setError(errorMessage(err));
  } finally {setBusy(false);}
 }
 return <main className="auth-screen"><section className="auth-hero"><Link className="logo" to="/feed">velo.</Link><h1>Больше, чем просто велосипед.</h1><p>Люди, маршруты и опыт, которые делают каждую поездку лучше.</p><img className="landscape auth-cycling-photo" src="/login-cycling.jpg" alt="Два велосипедиста на шоссейной гонке"/><p>Сообщество велосипедистов</p></section>
 <section className="auth-form"><h1>{registration ? 'Создать аккаунт' : 'С возвращением!'}</h1><p className="subtitle">{registration ? 'Присоединяйтесь к сообществу велосипедистов' : 'Войдите, чтобы поделиться своей историей'}</p>
 <form onSubmit={submit}>{error && <p className="error" role="alert">{error}</p>}
 {registration && <Input label="Имя пользователя" name="username" required minLength={3} maxLength={50} pattern="[a-zA-Z0-9_]+" title="Латинские буквы, цифры и _" autoComplete="username" disabled={busy}/>}
 <Input label="Email" type="email" name="email" required maxLength={254} autoComplete="email" placeholder="minh@example.com" disabled={busy} onChange={() => setPasswordError('')}/>
 <Input label="Пароль" type="password" name="password" required minLength={registration ? 8 : undefined} maxLength={128} autoComplete={registration ? 'new-password' : 'current-password'} disabled={busy}
  aria-invalid={passwordError ? true : undefined} aria-describedby={passwordError ? 'login-password-error' : undefined} onChange={() => setPasswordError('')}/>
 {passwordError && <p id="login-password-error" className="error" role="alert">{passwordError}</p>}
 {registration && <Input label="Подтвердите пароль" type="password" name="confirm" required autoComplete="new-password" disabled={busy}/>}
 {!registration && <label><input type="checkbox" name="remember" disabled={busy}/> Запомнить меня</label>}
 <button className="velo-button" type="submit" disabled={busy}>{busy ? 'Подождите...' : registration ? 'Создать аккаунт' : 'Войти'}</button></form>
 <hr/><p className="subtitle">{registration ? 'Уже есть аккаунт?' : 'Впервые здесь?'}</p><Link className="velo-button secondary" to={registration ? '/login' : '/register'}>{registration ? 'Войти' : 'Создать аккаунт'}</Link><Link className="velo-button secondary" to="/feed">Посмотреть ленту</Link></section></main>;
}
