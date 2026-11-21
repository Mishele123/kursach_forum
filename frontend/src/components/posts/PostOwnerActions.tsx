import { useEffect, useId, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { errorMessage, postsApi } from '../../services/api';
import type { Post, PostCategory, PostPlace } from '../../types';
import { CATEGORY_LABELS, POST_CATEGORIES } from '../../utils/constants';
import ContentActions from '../common/ContentActions';
import { PostLocationField } from './PostLocation';

type Action = 'edit' | 'delete';

export interface PostMutationProps {
  onUpdate: (post: Post) => void;
  onDelete: (id: number) => void;
}

export default function PostOwnerActions({ post, onUpdate, onDelete }: PostMutationProps & {
  post: Post;
}) {
  const [action, setAction] = useState<Action | null>(null);

  return <>
    <ContentActions className="post-card-menu" label="Действия с публикацией">{choose => <>
      <button type="button" onClick={() => choose(() => setAction('edit'))}>Редактировать</button>
      <button type="button" className="post-danger-text" onClick={() => choose(() => setAction('delete'))}>
        Удалить
      </button>
    </>}</ContentActions>
    {action && <PostActionDialog action={action} post={post} onUpdate={onUpdate}
      onDelete={onDelete} onClose={() => setAction(null)} />}
  </>;
}

function PostActionDialog({ action, post, onUpdate, onDelete, onClose }: PostMutationProps & {
  action: Action;
  post: Post;
  onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const pending = useRef(false);
  const heading = useId();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [place, setPlace] = useState<PostPlace | null>();
  const editing = action === 'edit';

  useEffect(() => {
    const element = dialog.current;
    element?.showModal();
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending.current) return;

    const form = new FormData(event.currentTarget);
    const data = {
      title: String(form.get('title') ?? '').trim(),
      text: String(form.get('text') ?? '').trim(),
      category: form.get('category') as PostCategory,
      ...(place !== undefined ? { place } : {}),
    };
    if (editing && (!data.title || !data.text)) {
      setError('Введите заголовок и текст публикации.');
      return;
    }

    pending.current = true;
    setBusy(true);
    setError('');
    try {
      if (editing) {
        const updated = await postsApi.updatePost(post.id, data);
        dialog.current?.close();
        onUpdate(updated);
      } else {
        await postsApi.deletePost(post.id);
        dialog.current?.close();
        onDelete(post.id);
      }
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }

  return <dialog ref={dialog} className="post-action-dialog" aria-labelledby={heading} onClose={onClose}
    onCancel={event => { if (pending.current) event.preventDefault(); }}>
    <h3 id={heading}>{editing ? 'Редактировать публикацию' : 'Удалить публикацию?'}</h3>
    <button type="button" className="post-dialog-close" aria-label="Закрыть" disabled={busy}
      onClick={() => dialog.current?.close()}>×</button>
    <form onSubmit={submit} aria-busy={busy}>
      {editing ? <fieldset disabled={busy} className="post-edit-fields">
        <label>Заголовок<input name="title" defaultValue={post.title} required maxLength={200} autoFocus /></label>
        <label>Категория<select name="category" defaultValue={post.category}>
          {POST_CATEGORIES.map(category => <option key={category} value={category}>{CATEGORY_LABELS[category]}</option>)}
        </select></label>
        <label>Текст публикации<textarea name="text" defaultValue={post.text} required maxLength={10000} rows={5} /></label>
        <PostLocationField place={place === undefined ? post.place : place} onChange={setPlace} />
      </fieldset> : <p>Публикация «{post.title}» и её комментарии будут удалены.</p>}
      {error && <p role="alert" className="error">{error}</p>}
      <div className="post-dialog-actions">
        <button type="button" className="velo-button secondary" autoFocus={!editing} disabled={busy}
          onClick={() => dialog.current?.close()}>Отмена</button>
        <button type="submit" className={`velo-button${editing ? '' : ' post-danger-button'}`} disabled={busy}>
          {editing ? (busy ? 'Сохраняем…' : 'Сохранить') : (busy ? 'Удаляем…' : 'Удалить')}
        </button>
      </div>
    </form>
  </dialog>;
}
