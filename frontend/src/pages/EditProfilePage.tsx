import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi, errorMessage, uploadPhoto } from '../services/api';
import { Input, Textarea, Button } from '../components/common';
import AvatarImage from '../components/common/AvatarImage';
export default function EditProfilePage() {
  const { user, refreshUser } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [photo, setPhoto] = useState<File | null>(null);
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || null);
  const [preview, setPreview] = useState('');
  const fileInput = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (!photo) { setPreview(''); return; }
    const url = URL.createObjectURL(photo);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [photo]);
  const navigate = useNavigate();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError('');
    const data = new FormData(event.currentTarget);
    try {
      const username = String(data.get('username')).trim();
      if (username.length < 3) { setError('Имя должно содержать от 3 до 50 символов'); return; }
      const avatar_url = photo ? await uploadPhoto(photo) : avatarUrl;
      if (photo) { setAvatarUrl(avatar_url); setPhoto(null); }
      await authApi.updateProfile({
        ...Object.fromEntries(['city','discipline','interests','bio'].map(key => [key, String(data.get(key)).trim()])),
        username, avatar_url,
      });
      await refreshUser(); navigate('/profile');
    } catch (err) { setError(errorMessage(err)); } finally { setBusy(false); }
  }
  return <section className="velo-page"><h1>Редактирование профиля</h1><p className="subtitle">Настройте профиль, чтобы находить единомышленников</p>
    <form onSubmit={submit} className="velo-card velo-form">
      {error && <p className="error" role="alert">{error}</p>}
      <fieldset className="profile-fields" disabled={busy}>
      <div className="profile-avatar-editor">
        <div className="avatar large"><AvatarImage username={user?.username || '?'} url={preview || avatarUrl} /></div>
        <div><label htmlFor="profile-avatar">Фото профиля</label>
          <p className="subtitle">JPG, PNG, GIF, WEBP · до 5 МБ</p>
          <input ref={fileInput} id="profile-avatar" type="file" accept="image/jpeg,image/png,image/gif,image/webp" onChange={event => {
            const file = event.target.files?.[0] || null;
            if (file && (file.size > 5*1024*1024 || !['image/jpeg','image/png','image/gif','image/webp'].includes(file.type))) {
              setError('Выберите JPG, PNG, GIF или WEBP размером до 5 МБ'); event.target.value = ''; setPhoto(null); return;
            }
            setError(''); setPhoto(file);
          }} />
          {(photo || avatarUrl) && <button className="avatar-remove" type="button" onClick={() => {
            setPhoto(null); setAvatarUrl(null); setError(''); if (fileInput.current) fileInput.current.value = '';
          }}>Убрать фото</button>}
        </div>
      </div>
      <Input name="username" label="Имя пользователя" defaultValue={user?.username || ''} required minLength={3} maxLength={50} autoComplete="username" />
      <Input name="city" label="Город" maxLength={100} defaultValue={user?.city || ''} placeholder="Самара" />
      <Input name="discipline" label="Дисциплина" list="disciplines" maxLength={100} defaultValue={user?.discipline || ''} placeholder="MTB" />
      <datalist id="disciplines">{['MTB','Шоссе','Гравий','BMX','Городской'].map(d => <option key={d} value={d} />)}</datalist>
      <Input name="interests" label="Интересы" maxLength={500} defaultValue={user?.interests || ''} placeholder="Маршруты, апгрейд, велопутешествия" />
      <Textarea name="bio" label="О себе" maxLength={1000} defaultValue={user?.bio || ''} rows={4} />
      </fieldset>
      <div className="form-actions"><Button type="submit" isLoading={busy}>Сохранить изменения</Button><Link className="velo-button secondary" to="/profile">Отмена</Link></div>
    </form></section>;
}
