import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi, errorMessage } from '../services/api';
import { Input, Textarea, Button } from '../components/common';
export default function EditProfilePage() {
 const {user,refreshUser}=useAuth(); const navigate=useNavigate();
 const [busy,setBusy]=useState(false); const [error,setError]=useState('');
 async function submit(e:FormEvent<HTMLFormElement>) {
  e.preventDefault(); const data=new FormData(e.currentTarget); setError('');
  const interests=String(data.get('interests')).split(',').map(x=>x.trim()).filter(Boolean);
  if(interests.length>20 || interests.some(x=>x.length>80)) {setError('Не более 20 интересов, каждый до 80 символов');return;}
  setBusy(true); try {await authApi.updateProfile({city:String(data.get('city')).trim()||null,discipline:String(data.get('discipline')).trim()||null,bio:String(data.get('bio')).trim()||null,interests}); await refreshUser(); navigate('/profile');} catch(err){setError(errorMessage(err));}finally{setBusy(false);}
 }
 return <section className="velo-page"><h1>Редактирование профиля</h1><form className="velo-card velo-form" onSubmit={submit}>
 {error && <p role="alert" className="error">{error}</p>}<fieldset disabled={busy} className="profile-fields">
 <p>Имя пользователя: {user?.username}</p>
 <Input name="city" label="Город" maxLength={100} defaultValue={user?.city||''}/>
 <Input name="discipline" label="Дисциплина" maxLength={100} defaultValue={user?.discipline||''}/>
 <Textarea name="interests" label="Интересы (через запятую)" defaultValue={user?.interests.join(', ')||''}/>
 <Textarea name="bio" label="О себе" maxLength={2000} defaultValue={user?.bio||''}/>
 </fieldset><div className="form-actions"><Button type="submit" isLoading={busy}>Сохранить изменения</Button><Link to="/profile">Отмена</Link></div></form></section>;
}
