import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { commentsApi, errorMessage } from '../../services/api';
import { formatRelativeTime } from '../../utils/helpers';
import AvatarImage from '../common/AvatarImage';
import type { Comment } from '../../types';

export default function Comments({ postId }: { postId: number }) {
 const { user, isLoading: authLoading } = useAuth();
 const [items, setItems] = useState<Comment[]>([]);
 const [cursor, setCursor] = useState<number>();
 const [next, setNext] = useState<number | null>(null);
 const [loading, setLoading] = useState(true);
 const [loadError, setLoadError] = useState('');
 const [retry, setRetry] = useState(0);
 const [text, setText] = useState('');
 const [sending, setSending] = useState(false);
 const [sendError, setSendError] = useState('');
 const [notice, setNotice] = useState('');
 const alive = useRef(true);
 useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
 useEffect(() => {
  let active = true;
  setLoading(true); setLoadError('');
  void commentsApi.getComments(postId, cursor).then(page => {
   if (!active) return;
   setItems(old => [...old, ...page.items.filter(c => !old.some(existing => existing.id === c.id))].sort((a,b) => b.id - a.id));
   setNext(page.next_cursor);
  }).catch(error => { if(active) setLoadError(errorMessage(error)); })
    .finally(() => { if(active) setLoading(false); });
  return () => { active = false; };
 }, [postId, cursor, retry]);
 async function submit(event: FormEvent) {
  event.preventDefault();
  if(sending || !text.trim()) return;
  setSending(true); setSendError(''); setNotice('');
  try {
   const comment = await commentsApi.createComment(postId, text.trim());
   if(!alive.current) return;
   setItems(old => [comment, ...old.filter(c => c.id !== comment.id)]);
   setText(''); setNotice('Комментарий опубликован');
  } catch(error) { if(alive.current) setSendError(errorMessage(error)); }
  finally { if(alive.current) setSending(false); }
 }
 return <section className="velo-card comments-panel" aria-labelledby="comments-heading">
  <div className="comments-heading"><h2 id="comments-heading">Комментарии</h2>
   {!!items.length && <span className="comments-count" title="Количество загруженных комментариев" aria-label={`Загружено комментариев: ${items.length}${next !== null ? ', есть ещё' : ''}`}>{items.length}{next !== null ? '+' : ''}</span>}
  </div>
  <p className="subtitle">Обсудите маршрут и поделитесь опытом</p>
  {authLoading ? <p role="status">Проверка входа…</p> : user ?
   <form className="velo-form comment-composer" onSubmit={submit}>
    <label className="sr-only" htmlFor="comment-text">Ваш комментарий</label>
    <textarea id="comment-text" rows={3} maxLength={3000} required disabled={sending}
      value={text} onChange={e => {setText(e.target.value); setNotice('');}} placeholder="Напишите комментарий…"/>
    {sendError && <p role="alert" className="error">{sendError}</p>}
    <div className="comment-composer-actions"><small>{text.length} / 3000</small><button className="velo-button" type="submit" disabled={sending || !text.trim()}>{sending ? 'Отправляем…' : 'Отправить'}</button></div>
    {notice && <p role="status">{notice}</p>}
   </form> : <p className="comments-login"><Link to="/login">Войдите</Link>, чтобы оставить комментарий.</p>}
  {loadError && <p role="alert" className="error">{loadError} <button type="button" onClick={() => setRetry(n => n + 1)}>Повторить загрузку</button></p>}
  <div className="comments-list">{items.map(comment => <article className="comment-item" key={comment.id}>
   <Link className="avatar comment-avatar" to={`/users/${comment.author.id}`} aria-label={`Профиль ${comment.author.username}`}><AvatarImage username={comment.author.username} url={comment.author.avatar_url}/></Link>
   <div className="comment-content"><header><Link className="comment-author" to={`/users/${comment.author.id}`}><strong>{comment.author.username}</strong></Link><time dateTime={comment.created_at} title={new Date(comment.created_at).toLocaleString('ru-RU')}>{formatRelativeTime(comment.created_at)}</time></header>
   <p>{comment.text}</p></div>
  </article>)}</div>
  {loading && <p role="status">Загрузка комментариев…</p>}
  {!loading && !loadError && !items.length && <p className="subtitle">Комментариев пока нет. Начните обсуждение!</p>}
  {next !== null && !loadError && <button type="button" className="velo-button secondary" disabled={loading} onClick={() => {if(next !== null) setCursor(next);}}>Загрузить ещё комментарии</button>}
 </section>;
}
