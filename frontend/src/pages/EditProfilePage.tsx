import AccountSettings from '../components/AccountSettings';
import AvatarEditor from '../components/AvatarEditor';
import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi, errorMessage } from '../services/api';
import { Input, Textarea, Button } from '../components/common';
import AvatarImage from '../components/common/AvatarImage';
import Landscape from '../components/common/Landscape';
import './EditProfilePage.css';

type Tab = 'profile' | 'security';
const suggestions = ['Гравел', 'Путешествия', 'Город', 'Шоссе', 'MTB'];

export default function EditProfilePage() {
  const { user, refreshUser } = useAuth();
  const [tab, setTab] = useState<Tab>('profile');
  const [city, setCity] = useState(user?.city || '');
  const [discipline, setDiscipline] = useState(user?.discipline || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [interests, setInterests] = useState<string[]>(user?.interests || []);
  const [newInterest, setNewInterest] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const dirty = city !== (user?.city || '') || discipline !== (user?.discipline || '') || bio !== (user?.bio || '') || JSON.stringify(interests) !== JSON.stringify(user?.interests || []);
  function toggleInterest(value: string) {
    setNotice('');
    if (interests.includes(value)) setInterests(interests.filter(item => item !== value));
    else if (interests.length < 20) { setInterests([...interests, value]); setError(''); }
    else setError('Не более 20 интересов, каждый до 80 символов');
  }
  function addInterest() {
    const value = newInterest.trim();
    if (!value) return;
    if (value.length > 80 || interests.length >= 20) { setError('Не более 20 интересов, каждый до 80 символов'); return; }
    if (!interests.includes(value)) setInterests([...interests, value]);
    setNewInterest(''); setError(''); setNotice('');
  }
  function reset() {
    setCity(user?.city || ''); setDiscipline(user?.discipline || ''); setBio(user?.bio || '');
    setInterests(user?.interests || []); setNewInterest(''); setError(''); setNotice('');
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(''); setNotice('');
    if (newInterest.trim()) { setError('Добавьте новый интерес кнопкой «Добавить» или очистите поле.'); return; }
    setBusy(true);
    try {
      await authApi.updateProfile({ city: city.trim() || null, discipline: discipline.trim() || null, bio: bio.trim() || null, interests });
      await refreshUser(); setCity(city.trim()); setDiscipline(discipline.trim()); setBio(bio.trim());
      setNotice('Изменения сохранены');
    } catch (err) { setError(errorMessage(err)); } finally { setBusy(false); }
  }
  return <section className="velo-page settings-page profile-redesign">
    <Link className="back-link" to="/profile">⌂ <span>›</span> Мой профиль</Link>
    <header className="page-heading"><div><h1>Настройки профиля</h1><p className="subtitle">Обновите информацию о себе — она будет видна другим участникам сообщества.</p></div><Link className="profile-view-link" to="/profile">↗ Посмотреть профиль</Link></header>
    <div className="profile-settings-grid"><div className="profile-settings-editor">
      <nav className="profile-tabs" aria-label="Разделы настроек">{([['profile', 'Профиль'], ['security', 'Смена пароля']] as const).map(([id, label]) => <button key={id} type="button" aria-current={tab === id ? 'page' : undefined} onClick={() => setTab(id)}>{label}</button>)}</nav>
      <div hidden={tab !== 'profile'}>
        <AvatarEditor />
        <form className="profile-about-form" onSubmit={submit}>
          <div className="velo-card velo-form profile-about-card"><div><h2>Расскажите о себе</h2><p className="subtitle">Найдите тех, кто разделяет ваш ритм и маршруты.</p></div>
            <fieldset disabled={busy} className="profile-fields">
              <div className="profile-location-grid"><Input label="Город" name="city" maxLength={100} placeholder="Ваш город" value={city} onChange={e => { setCity(e.target.value); setNotice(''); }} /><Input label="Дисциплина" name="discipline" maxLength={100} placeholder="Например, гравел" value={discipline} onChange={e => { setDiscipline(e.target.value); setNotice(''); }} /></div>
              <div className="profile-interest-field"><span className="interest-label">Интересы <small>{interests.length}/20</small></span><div className="interest-chips">{[...new Set([...interests, ...suggestions])].map(value => <button key={value} type="button" aria-pressed={interests.includes(value)} onClick={() => toggleInterest(value)}>{value}{interests.includes(value) && <span aria-hidden="true"> ✓</span>}</button>)}</div>
                <div className="interest-add"><Input label="Свой интерес" maxLength={80} value={newInterest} placeholder="Что вам нравится?" onChange={e => setNewInterest(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addInterest(); } }} /><button type="button" onClick={addInterest} disabled={!newInterest.trim()}>+ Добавить</button></div>
              </div>
              <div><Textarea label="О себе" name="bio" maxLength={2000} rows={4} placeholder="Расскажите, где любите кататься и какие маршруты вас вдохновляют…" value={bio} onChange={e => { setBio(e.target.value); setNotice(''); }} /><p className="bio-counter">{bio.length} / 2000</p></div>
            </fieldset>
          </div>
          {error && <p role="alert" className="error">{error}</p>}
          <div className="profile-save-bar"><Button type="submit" disabled={!dirty || busy} isLoading={busy}>Сохранить изменения</Button><button type="button" className="profile-cancel" disabled={busy} onClick={reset}>Отмена</button><span role="status" className={dirty ? 'save-status unsaved' : 'save-status'}>{notice || (dirty ? 'Есть несохранённые изменения' : 'Все изменения сохранены')}</span></div>
        </form>

      </div>
      <div hidden={tab === 'profile'}><AccountSettings /></div>
    </div>
    <aside className="profile-live-preview" aria-label="Предпросмотр профиля"><h2>Так выглядит ваш профиль</h2><article className="profile-preview-card"><div className="preview-cover"><Landscape /></div><div className="preview-details"><div className="avatar preview-avatar"><AvatarImage username={user?.username || ''} url={user?.avatar_url} /></div><h3>{user?.username}</h3><p className="preview-city">⌖ {city.trim() || 'Город не указан'}</p>{discipline.trim() && <span className="preview-discipline">{discipline}</span>}<p className="preview-bio">{bio.trim() || 'Здесь появится ваш рассказ о себе и любимых маршрутах.'}</p>{interests.length > 0 && <div className="preview-interests">{interests.map(item => <span key={item}>{item}</span>)}</div>}<Link className="preview-bike-link" to="/bikes"><div><strong>Мои велосипеды</strong><small>Ваша история на двух колёсах</small></div><span aria-hidden="true">›</span></Link></div></article><div className="preview-privacy"><span aria-hidden="true">ⓘ</span><p>Информация профиля помогает другим участникам узнать вас.<small>Не указывайте личные данные, которыми не хотите делиться.</small></p></div></aside>
    </div>
  </section>;
}
