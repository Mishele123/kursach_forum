import { useEffect, useId, useRef, useState } from 'react';

interface PhotoPickerProps {
  files: File[];
  onChange: (files: File[]) => void;
  disabled?: boolean;
  maximum?: number;
}

export default function PhotoPicker({ files, onChange, disabled, maximum = 10 }: PhotoPickerProps) {
  const id = useId();
  const input = useRef<HTMLInputElement>(null);
  const [error, setError] = useState('');
  const [urls, setUrls] = useState<string[]>([]);

  useEffect(() => {
    const next = files.map(file => URL.createObjectURL(file));
    setUrls(next);
    return () => next.forEach(url => URL.revokeObjectURL(url));
  }, [files]);

  return <div className="upload-area">
    <label className="photo-picker-label" htmlFor={id}>Фотографии</label>
    <input ref={input} id={id} className="photo-picker-input" type="file" hidden
      accept="image/jpeg,image/png" multiple={maximum > 1} disabled={disabled}
      aria-describedby={`${id}-hint`} aria-invalid={!!error}
      onChange={event => {
        const next = Array.from(event.target.files || []);
        const message = next.length > maximum ? `Не более ${maximum} фото`
          : next.some(file => file.size > 5 * 1024 * 1024 || !['image/jpeg', 'image/png'].includes(file.type))
            ? 'Выберите JPEG или PNG до 5 МБ каждый' : '';
        setError(message);
        if (!message) onChange(next);
        event.target.value = '';
      }} />
    <div className="photo-picker-controls">
      <button className="photo-picker-button" type="button" disabled={disabled}
        aria-controls={id} aria-describedby={`${id}-hint ${id}-files`}
        onClick={() => input.current?.click()}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
          <path d="M16 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V8" />
          <path d="M19 1v6M16 4h6M3 16l5-5 5 5 4-4 4 4" />
          <circle cx="8.5" cy="7.5" r="1.5" />
        </svg>
        <span>Добавить фото</span>
      </button>
      <span id={`${id}-files`} className="photo-picker-filenames" role="status" aria-live="polite" aria-atomic="true">
        {files.length ? files.map(file => file.name).join(', ') : 'Файл не выбран'}
      </span>
    </div>
    <p id={`${id}-hint`}>JPEG, PNG · до 5 МБ и 20 мегапикселей каждый</p>
    {error && <p className="error" role="alert">{error}</p>}
    <div className="photo-previews">{urls.map((url, index) => <figure key={url}>
      <img src={url} alt={`Выбранное фото ${index + 1}`} />
      <button type="button" disabled={disabled} onClick={() => onChange(files.filter((_, i) => i !== index))}>
        Убрать фото {index + 1}
      </button>
    </figure>)}</div>
  </div>;
}
