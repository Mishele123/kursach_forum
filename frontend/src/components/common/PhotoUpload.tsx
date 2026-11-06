import { useRef, useState } from 'react';
import PhotoPicker from './PhotoPicker';
import { errorMessage } from '../../services/api';

interface PhotoUploadProps {
  upload: (files: File[]) => Promise<void>;
  label?: string;
  maximum?: number;
}

export default function PhotoUpload({ upload, label = 'Загрузить фото', maximum = 1 }: PhotoUploadProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const pending = useRef(false);

  async function submit() {
    if (pending.current || !files.length) return;
    pending.current = true;
    setBusy(true);
    setError('');
    setNotice('');
    try {
      await upload(files);
      setFiles([]);
      setNotice('Фотографии сохранены');
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }

  return <div className="photo-upload">
    <PhotoPicker files={files} onChange={next => {
      setFiles(next);
      setNotice('');
      setError('');
    }} disabled={busy} maximum={maximum} />
    <button type="button" className="velo-button secondary" disabled={busy || !files.length} onClick={submit}>
      {busy ? 'Загружаем…' : label}
    </button>
    {error && <p className="error" role="alert">{error}</p>}
    {notice && <p role="status">{notice}</p>}
  </div>;
}
