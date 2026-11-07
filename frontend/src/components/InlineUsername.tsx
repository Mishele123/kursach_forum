import { useEffect, useId, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { authApi, errorMessage } from '../services/api';

export default function InlineUsername() {
  const { user, refreshUser } = useAuth();
  const id = useId();
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const input = useRef<HTMLInputElement>(null);
  const pencil = useRef<HTMLButtonElement>(null);
  const pending = useRef(false);
  const interacted = useRef(false);

  useEffect(() => {
    if (editing) { input.current?.focus(); input.current?.select(); }
    else if (interacted.current) pencil.current?.focus();
  }, [editing]);

  function cancel() {
    if (pending.current) return;
    setError('');
    setEditing(false);
  }

  async function save(event: FormEvent) {
    event.preventDefault();
    if (!user || pending.current) return;
    const username = name.trim();
    if (!/^[a-zA-Z0-9_]{3,50}$/.test(username)) {
      setError('Введите 3–50 латинских букв, цифр или _');
      input.current?.focus();
      return;
    }
    if (username === user.username) { cancel(); return; }
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      await authApi.updateUsername(username);
      await refreshUser();
      setEditing(false);
      setNotice('Имя пользователя обновлено');
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }

  if (!user) return null;
  return <div className="inline-username">
    <h2 id="profile-name" className={editing ? 'sr-only' : undefined}>{user.username}</h2>
    {editing ? <form className="inline-username-form" onSubmit={save} onKeyDown={event => {
      if (event.key === 'Escape') { event.preventDefault(); cancel(); }
    }} aria-busy={busy}>
      <label className="sr-only" htmlFor={id}>Новое имя пользователя</label>
      <div className="inline-username-controls">
        <input ref={input} id={id} value={name} onChange={event => { setName(event.target.value); setError(''); }}
          required minLength={3} maxLength={50} pattern="[a-zA-Z0-9_]+" autoComplete="username"
          disabled={busy} aria-invalid={!!error} aria-describedby={`${id}-hint${error ? ` ${id}-error` : ''}`} />
        <button type="submit" className="username-save" disabled={busy} aria-label="Сохранить имя" title="Сохранить имя">
          {busy ? <span aria-hidden="true">…</span> : <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 6" /></svg>}
        </button>
        <button type="button" className="username-cancel" disabled={busy} onClick={cancel} aria-label="Отменить изменение имени" title="Отмена">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" /></svg>
        </button>
      </div>
      <p id={`${id}-hint`} className="username-hint">3–50 символов: латинские буквы, цифры и _</p>
      {error && <p id={`${id}-error`} className="username-error" role="alert">{error}</p>}
    </form> : <button ref={pencil} type="button" className="username-pencil" title="Изменить имя" aria-label="Изменить имя" onClick={() => {
      interacted.current = true;
      setName(user.username);
      setError('');
      setNotice('');
      setEditing(true);
    }}>
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m16 3 5 5M3 21l5-1L21 7a2.1 2.1 0 0 0-5-5L3 15z" /></svg>
    </button>}
    <span className="sr-only" role="status" aria-live="polite">{notice}</span>
  </div>;
}
