import { lazy, Suspense, useEffect, useId, useRef, useState } from 'react';
import type { PostPlace } from '../../types';
import type { MapPoint } from './LocationMap';
import './PostLocation.css';

const LocationMap = lazy(() => import('./LocationMap'));

function PinIcon() {
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" />
    <circle cx="12" cy="10" r="2.5" />
  </svg>;
}

function placeLabel(place: PostPlace) {
  return place.name || `${place.latitude.toFixed(5)}, ${place.longitude.toFixed(5)}`;
}

export function PostLocationField({ place, onChange }: {
  place: PostPlace | null | undefined;
  onChange: (place: PostPlace | null) => void;
}) {
  const [open, setOpen] = useState(false);

  return <div className="post-location-field">
    {place && <span className="post-location-label"><PinIcon />{placeLabel(place)}</span>}
    <button type="button" className="post-location-outline" aria-haspopup="dialog" onClick={() => setOpen(true)}>
      {!place && <PinIcon />}{place ? 'Изменить место' : 'Добавить место'}
    </button>
    {place && <button type="button" className="post-location-remove" onClick={() => onChange(null)}>Убрать</button>}
    {open && <LocationDialog place={place} onClose={() => setOpen(false)} onConfirm={onChange} />}
  </div>;
}

function LocationDialog({ place, onClose, onConfirm }: {
  place: PostPlace | null | undefined;
  onClose: () => void;
  onConfirm: (place: PostPlace) => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const title = useId();
  const [point, setPoint] = useState<MapPoint | null>(place ?? null);
  const [name, setName] = useState(place?.name ?? '');

  useEffect(() => { dialog.current?.showModal(); }, []);

  function confirm() {
    if (!point) return;
    dialog.current?.close();
    onConfirm({ latitude: point.latitude, longitude: point.longitude, name: name.trim() || null });
  }

  return <dialog ref={dialog} className="post-location-dialog" aria-labelledby={title}
    onClose={event => { event.stopPropagation(); onClose(); }}
    onKeyDown={event => { if (event.key === 'Enter' && event.target instanceof HTMLInputElement) event.preventDefault(); }}>
    <h3 id={title}>Выбрать место</h3>
    <button type="button" className="post-location-close" aria-label="Закрыть"
      onClick={() => dialog.current?.close()}>×</button>
    <p>Нажмите на карту, чтобы поставить метку. С клавиатуры используйте стрелки и Enter.</p>
    <Suspense fallback={<div className="post-location-map" role="status">Загрузка карты…</div>}>
      <LocationMap point={point} onPick={setPoint} />
    </Suspense>
    {point && <p className="post-location-coordinates" aria-live="polite">{placeLabel(point)}</p>}
    <label className="post-location-name">Название места (необязательно)
      <input value={name} onChange={event => setName(event.target.value)} maxLength={200} />
    </label>
    <div className="post-location-actions">
      <button type="button" className="velo-button secondary" onClick={() => dialog.current?.close()}>Отмена</button>
      <button type="button" className="velo-button" disabled={!point} onClick={confirm}>Подтвердить</button>
    </div>
  </dialog>;
}

export function PostLocationPreview({ place }: { place: PostPlace }) {
  const preview = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = preview.current;
    if (!node) return;
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        setVisible(true);
        observer.disconnect();
      }
    });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const mapUrl = `https://www.openstreetmap.org/?mlat=${place.latitude}&mlon=${place.longitude}#map=15/${place.latitude}/${place.longitude}`;
  return <div ref={preview} className="post-location-preview">
    <a className="post-location-label" href={mapUrl} target="_blank" rel="noopener">
      <PinIcon />{placeLabel(place)}
    </a>
    <div className="post-location-preview-map">
      {visible && <Suspense fallback={null}><LocationMap point={place} /></Suspense>}
    </div>
  </div>;
}
