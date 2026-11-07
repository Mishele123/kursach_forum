import {useRef,useState} from 'react';
import type {FormEvent} from 'react';
import {Link,useNavigate} from 'react-router-dom';
import {postsApi,errorMessage} from '../services/api';
import {Input,Button} from '../components/common';
import PhotoPicker from '../components/common/PhotoPicker';
import {POST_CATEGORIES,CATEGORY_LABELS} from '../utils/constants';
import type {PostCategory} from '../types';
export default function CreatePostPage(){
 const [files,setFiles]=useState<File[]>([]);const [busy,setBusy]=useState(false);const [error,setError]=useState('');const pending=useRef(false);const navigate=useNavigate();
 async function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();if(pending.current)return;const form=new FormData(e.currentTarget);const data={title:String(form.get('title')).trim(),text:String(form.get('text')).trim(),category:String(form.get('category')) as PostCategory};if(!data.title||!data.text){setError('Введите заголовок и текст публикации');return;}pending.current=true;setBusy(true);setError('');try{const post=files.length?await postsApi.createWithPhotos(data,files):await postsApi.createPost(data);navigate(`/post/${post.id}`);}catch(err){setError(errorMessage(err));}finally{pending.current=false;setBusy(false);}}
 return <section className="velo-page"><h1>Создать публикацию</h1><p className="subtitle">Поделитесь историей, маршрутом или полезным опытом</p><form className="velo-card velo-form" onSubmit={submit}>{error&&<p role="alert" className="error">{error}</p>}<fieldset className="profile-fields" disabled={busy}><Input label="Заголовок *" name="title" required maxLength={200}/><label>Категория *<select name="category" defaultValue="route">{POST_CATEGORIES.map(c=><option key={c} value={c}>{CATEGORY_LABELS[c]}</option>)}</select></label><label>Текст публикации *<textarea name="text" rows={9} required maxLength={10000}/></label><PhotoPicker files={files} onChange={setFiles} disabled={busy}/></fieldset><div className="form-actions"><Button type="submit" isLoading={busy}>Опубликовать</Button><Link to="/feed">Отмена</Link></div></form></section>;
}
