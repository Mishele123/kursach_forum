import { useEffect, useId, useRef, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { errorMessage } from '../../services/api';

export default function ModerationDialog({ title, children, confirm, destructive = false,
  disabled = false, onSubmit, onSuccess, onClose }: {
  title: string;
  children: ReactNode;
  confirm: string;
  destructive?: boolean;
  disabled?: boolean;
  onSubmit: () => Promise<unknown>;
  onSuccess: () => void;
  onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const heading = useId();
  const pending = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { dialog.current?.showModal(); }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending.current || disabled) return;
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      await onSubmit();
      dialog.current?.close();
      onSuccess();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }

  return <dialog ref={dialog} className="post-action-dialog moderation-dialog" aria-labelledby={heading}
    onClose={onClose} onCancel={event => { if (pending.current) event.preventDefault(); }}>
    <h3 id={heading}>{title}</h3>
    <button type="button" className="post-dialog-close" aria-label="Закрыть" disabled={busy}
      onClick={() => dialog.current?.close()}>×</button>
    <form onSubmit={submit} aria-busy={busy}>
      <fieldset disabled={busy}>{children}</fieldset>
      {error && <p className="error" role="alert">{error}</p>}
      <div className="post-dialog-actions">
        <button type="button" className="velo-button secondary" autoFocus disabled={busy}
          onClick={() => dialog.current?.close()}>Отмена</button>
        <button type="submit" className={`velo-button${destructive ? ' post-danger-button' : ''}`}
          disabled={busy || disabled}>{busy ? 'Подождите…' : confirm}</button>
      </div>
    </form>
  </dialog>;
}
