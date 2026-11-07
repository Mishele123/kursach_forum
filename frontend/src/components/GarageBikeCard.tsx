import { useRef, useState } from 'react';
import BikeImage from './common/BikeImage';
import PhotoPicker from './common/PhotoPicker';
import { bikesApi, errorMessage } from '../services/api';
import type { Bike } from '../types';

export default function GarageBikeCard({ bike, onSaved }: { bike: Bike; onSaved: () => Promise<void> }) {
  const [editing, setEditing] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const pending = useRef(false);
  function cancel() { if (!pending.current) { setEditing(false); setFiles([]); setError(''); } }
  async function save() {
    if (pending.current || !files.length) return;
    pending.current = true; setBusy(true); setError('');
    try {
      await bikesApi.uploadPhoto(bike.id, files[0]);
      setFiles([]); setEditing(false);
      await onSaved();
    } catch (err) { setError(errorMessage(err)); }
    finally { pending.current = false; setBusy(false); }
  }
  return <article className="velo-card garage-bike-card">
    <div className="garage-bike-image"><BikeImage bike={bike} /></div>
    <div className="garage-bike-body"><div className="garage-bike-title"><h2>{bike.brand} {bike.model}</h2><span>{bike.year}<span className="sr-only"> · Год выпуска</span></span></div>
      <button type="button" className={`garage-photo-toggle ${!bike.photo_url ? 'garage-photo-add' : ''}`} aria-expanded={editing} disabled={busy} onClick={() => editing ? cancel() : setEditing(true)}>
        <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8" cy="8" r="1.5"/><path d="m3 17 6-6 4 4 3-3 5 5"/></svg>{bike.photo_url ? 'Изменить фото' : '+ Добавить фото'}
      </button>
      {editing && <div className="garage-photo-editor"><PhotoPicker files={files} onChange={next => { setFiles(next); setError(''); }} disabled={busy} maximum={1} />
        {error && <p role="alert" className="error">{error}</p>}
        <div className="garage-upload-actions"><button type="button" className="velo-button" disabled={busy || !files.length} onClick={save}>{busy ? 'Сохраняем…' : 'Сохранить фото'}</button><button type="button" className="garage-upload-cancel" disabled={busy} onClick={cancel}>Отмена</button></div>
      </div>}
    </div>
  </article>;
}
