import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi, errorMessage } from '../services/api';
import { Input, Textarea, Button } from '../components/common';
export default function EditProfilePage() {
  const { user, refreshUser } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError('');
    const data = new FormData(event.currentTarget);
    try {
      await authApi.updateProfile(Object.fromEntries(['city','discipline','interests','bio'].map(key => [key, String(data.get(key)).trim()])));
      await refreshUser(); navigate('/profile');
    } catch (err) { setError(errorMessage(err)); } finally { setBusy(false); }
  }
  return <section className="velo-page"><h1>Редактирование профиля</h1><p className="subtitle">Настройте профиль, чтобы находить единомышленников</p>
    <form onSubmit={submit} className="velo-card velo-form">
      <div className="avatar large">{user?.username.slice(0,2).toUpperCase()}</div>
      {error && <p className="error" role="alert">{error}</p>}
      <Input label="Имя пользователя" value={user?.username || ''} readOnly />
      <Input name="city" label="Город" maxLength={100} defaultValue={user?.city || ''} placeholder="Самара" />
      <Input name="discipline" label="Дисциплина" list="disciplines" maxLength={100} defaultValue={user?.discipline || ''} placeholder="MTB" />
      <datalist id="disciplines">{['MTB','Шоссе','Гравий','BMX','Городской'].map(d => <option key={d} value={d} />)}</datalist>
      <Input name="interests" label="Интересы" maxLength={500} defaultValue={user?.interests || ''} placeholder="Маршруты, апгрейд, велопутешествия" />
      <Textarea name="bio" label="О себе" maxLength={1000} defaultValue={user?.bio || ''} rows={4} />
      <div className="form-actions"><Button type="submit" isLoading={busy}>Сохранить изменения</Button><Link className="velo-button secondary" to="/profile">Отмена</Link></div>
    </form></section>;
}
