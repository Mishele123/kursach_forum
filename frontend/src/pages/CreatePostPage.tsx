import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { postsApi, errorMessage } from '../services/api';
import { Input, Button } from '../components/common';
import { POST_CATEGORIES, CATEGORY_LABELS } from '../utils/constants';
import type { PostCategory } from '../types';
export default function CreatePostPage() {
 const [title,setTitle] = useState(''); const [text,setText] = useState('');
 const [category,setCategory] = useState<PostCategory>('route');
 const [photo,setPhoto] = useState<File | null>(null); const [preview,setPreview] = useState('');
 const [busy,setBusy] = useState(false); const [error,setError] = useState('');
 const [createdId,setCreatedId]=useState<number | null>(null); const fileInput=useRef<HTMLInputElement>(null); const navigate=useNavigate();
 useEffect(() => { if(!photo) {setPreview('');return;} const url=URL.createObjectURL(photo);setPreview(url);return () => URL.revokeObjectURL(url); },[photo]);
 async function submit(event: FormEvent) {
  event.preventDefault(); setError(''); if(!title.trim() || !text.trim()) {setError('Введите заголовок и текст публикации');return;}
  setBusy(true); try {
   const id=createdId ?? (await postsApi.createPost({title:title.trim(),text:text.trim(),category})).id;
   setCreatedId(id);
   if(photo) await postsApi.uploadPhoto(id,photo);
   navigate(`/post/${id}`);
  } catch(err) {setError(errorMessage(err));} finally {setBusy(false);}

 }
 return <section className="velo-page"><h1>Создать публикацию</h1><p className="subtitle">Поделитесь историей, маршрутом или полезным опытом</p><form className="velo-card velo-form" onSubmit={submit}>
 {error && <p role="alert" className="error">{error}</p>}
 <Input label="Заголовок *" placeholder="Выходные на двух колёсах" value={title} onChange={e=>setTitle(e.target.value)} required maxLength={200} disabled={busy || createdId!==null}/>
 <fieldset disabled={busy || createdId!==null}><legend>Категория *</legend><div className="category-tabs">{POST_CATEGORIES.map(c=><button key={c} type="button" aria-pressed={category===c} className={category===c?'selected':''} onClick={()=>setCategory(c)}>{CATEGORY_LABELS[c]}</button>)}</div></fieldset>
 <div><label htmlFor="post-text">Текст публикации *</label><textarea id="post-text" rows={9} value={text} onChange={e=>setText(e.target.value)} required maxLength={10000} disabled={busy || createdId!==null}/><small>{text.length} / 10000</small></div>
 <div className="upload-area"><label htmlFor="post-photo">+ Добавьте одну фотографию</label><p>JPG, PNG · до 5 МБ</p><input ref={fileInput} id="post-photo" type="file" accept="image/jpeg,image/png" disabled={busy} onChange={event=>{const file=event.target.files?.[0];if(file && (file.size>5*1024*1024 || !['image/jpeg','image/png'].includes(file.type))) {setError('Выберите изображение до 5 МБ');event.target.value='';setPhoto(null);return;}setError('');setPhoto(file||null);}}/>
 {preview && <><img className="upload-preview" src={preview} alt="Предпросмотр фотографии"/><button type="button" disabled={busy} onClick={()=>{setPhoto(null);if(fileInput.current) fileInput.current.value='';}}>Убрать фотографию</button></>}</div>
 {createdId!==null && <p role="status">Текст публикации сохранён. Повторите загрузку фотографии или <Link to={`/post/${createdId}`}>откройте публикацию без фото</Link>.</p>}<div className="form-actions"><Button type="submit" isLoading={busy}>{createdId!==null?'Повторить загрузку фото':'Опубликовать'}</Button><Link className="velo-button secondary" to="/feed">Отмена</Link></div></form></section>;
}
