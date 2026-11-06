import { useEffect, useRef, useState } from 'react';
import type { PointerEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { authApi, errorMessage } from '../services/api';
import AvatarImage from './common/AvatarImage';

const SIZE = 320;
const MAX_BYTES = 5 * 1024 * 1024;
interface Source { image: HTMLImageElement; url: string }
interface Position { x: number; y: number }

export default function AvatarEditor() {
  const { user, refreshUser } = useAuth();
  const input = useRef<HTMLInputElement>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const choose = useRef<HTMLButtonElement>(null);
  const drag = useRef<{ x: number; y: number; position: Position } | null>(null);
  const pending = useRef(false);
  const selection = useRef(0);
  const [source, setSource] = useState<Source | null>(null);
  const [zoom, setZoom] = useState(1);
  const [position, setPosition] = useState<Position>({ x: 0, y: 0 });
  const [draft, setDraft] = useState<File | null>(null);
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [cropError, setCropError] = useState('');
  const [notice, setNotice] = useState('');

  useEffect(() => () => { selection.current += 1; }, []);
  useEffect(() => {
    if (!draft) { setPreview(''); return; }
    const url = URL.createObjectURL(draft);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [draft]);
  useEffect(() => {
    const modal = dialog.current;
    if (source) { modal?.showModal(); }
    else if (modal?.open) { modal.close(); choose.current?.focus(); }
    return () => { if (source) URL.revokeObjectURL(source.url); };
  }, [source]);

  const scale = source ? SIZE / Math.min(source.image.naturalWidth, source.image.naturalHeight) * zoom : 1;
  const width = source ? source.image.naturalWidth * scale : SIZE;
  const height = source ? source.image.naturalHeight * scale : SIZE;
  function constrain(next: Position, nextZoom = zoom): Position {
    if (!source) return { x: 0, y: 0 };
    const ratio = SIZE / Math.min(source.image.naturalWidth, source.image.naturalHeight) * nextZoom;
    const maxX = Math.max(0, (source.image.naturalWidth * ratio - SIZE) / 2);
    const maxY = Math.max(0, (source.image.naturalHeight * ratio - SIZE) / 2);
    return { x: Math.max(-maxX, Math.min(maxX, next.x)), y: Math.max(-maxY, Math.min(maxY, next.y)) };
  }
  function changeZoom(value: number) {
    const next = Math.max(1, Math.min(3, value));
    setZoom(next);
    setPosition(old => constrain(old, next));
  }
  async function select(file?: File) {
    if (!file) return;
    const ticket = ++selection.current;
    setError(''); setNotice('');
    if (file.size > MAX_BYTES || !['image/jpeg', 'image/png'].includes(file.type)) {
      setError('Выберите JPEG или PNG до 5 МБ'); return;
    }
    setLoading(true);
    let url = '';
    try {
      const bytes = new Uint8Array(await file.slice(0, 8).arrayBuffer());
      const jpeg = bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255;
      const png = [137,80,78,71,13,10,26,10].every((value, index) => bytes[index] === value);
      if (!jpeg && !png) throw new Error('Выберите корректный JPEG или PNG');
      url = URL.createObjectURL(file);
      const image = new Image();
      image.src = url;
      await image.decode();
      if (!image.naturalWidth || !image.naturalHeight || image.naturalWidth * image.naturalHeight > 20_000_000) {
        throw new Error('Фотография должна быть не больше 20 мегапикселей');
      }
      if (ticket !== selection.current) { URL.revokeObjectURL(url); return; }
      setZoom(1); setPosition({ x: 0, y: 0 }); setCropError('');
      setSource({ image, url });
    } catch (err) {
      if (url) URL.revokeObjectURL(url);
      if (ticket === selection.current) setError(err instanceof Error ? err.message : 'Не удалось открыть изображение');
    } finally { if (ticket === selection.current) setLoading(false); }
  }
  function move(event: PointerEvent<HTMLDivElement>) {
    if (!drag.current || applying) return;
    const ratio = SIZE / event.currentTarget.getBoundingClientRect().width;
    setPosition(constrain({ x: drag.current.position.x + (event.clientX - drag.current.x) * ratio,
      y: drag.current.position.y + (event.clientY - drag.current.y) * ratio }));
  }
  async function apply() {
    if (!source || pending.current) return;
    pending.current = true; setApplying(true); setCropError('');
    try {
      const canvas = document.createElement('canvas');
      canvas.width = canvas.height = 512;
      const context = canvas.getContext('2d');
      if (!context) throw new Error('Не удалось обработать фото');
      context.drawImage(source.image, ((width - SIZE) / 2 - position.x) / scale,
        ((height - SIZE) / 2 - position.y) / scale, SIZE / scale, SIZE / scale, 0, 0, 512, 512);
      const blob = await new Promise<Blob>((resolve, reject) => canvas.toBlob(value => {
        if (value) resolve(value); else reject(new Error('Не удалось обработать фото'));
      }, 'image/jpeg', 0.92));
      setDraft(new File([blob], 'avatar-cropped.jpg', { type: 'image/jpeg' }));
      setSource(null); setNotice('');
    } catch (err) { setCropError(err instanceof Error ? err.message : 'Не удалось обработать фото'); }
    finally { pending.current = false; setApplying(false); }
  }
  async function save() {
    if (!draft || pending.current) return;
    pending.current = true; setSaving(true); setError(''); setNotice('');
    try {
      await authApi.uploadAvatar(draft);
      await refreshUser();
      setDraft(null); setNotice('Аватар сохранён');
    } catch (err) { setError(errorMessage(err)); }
    finally { pending.current = false; setSaving(false); }
  }

  return <section id="account-avatar" className="velo-card avatar-crop-card">
    <h2>Фото профиля</h2><p className="subtitle">Выберите фото, по которому вас узнают.</p>
    <div className="avatar-crop-layout">
      <div className="avatar avatar-crop-preview"><AvatarImage username={user?.username || ''} url={preview || user?.avatar_url}/></div>
      <div className="avatar-crop-controls">
        <input ref={input} type="file" className="photo-picker-input" hidden accept="image/jpeg,image/png" disabled={loading || saving}
          aria-label="Выбрать фото профиля" onChange={event => { const file = event.target.files?.[0]; event.target.value = ''; void select(file); }}/>
        {draft && <span className="avatar-preview-badge">Предпросмотр</span>}
        <button ref={choose} type="button" className="photo-picker-button" disabled={loading || saving} onClick={() => input.current?.click()}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M16 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V8M19 1v6M16 4h6M3 16l5-5 5 5 4-4 4 4"/><circle cx="8.5" cy="7.5" r="1.5"/></svg>
          <span>{loading ? 'Открываем…' : draft ? 'Выбрать другое фото' : 'Добавить фото'}</span>
        </button>
        <p className="avatar-crop-hint">JPEG / PNG · до 5 МБ и 20 Мп</p>
        {draft && <p className="avatar-draft-notice" role="status">Изменения ещё не сохранены</p>}
      </div>
    </div>
    {error && <p className="error" role="alert">{error}</p>}
    {notice && <p role="status">{notice}</p>}
    {draft && <div className="avatar-crop-actions"><button type="button" disabled={saving} onClick={() => { setDraft(null); setError(''); choose.current?.focus(); }}>Отмена</button>
      <button type="button" className="velo-button" disabled={saving} onClick={save}>{saving ? 'Сохраняем…' : 'Сохранить аватар'}</button></div>}

    <dialog ref={dialog} className="avatar-crop-dialog" aria-labelledby="avatar-crop-title" aria-describedby="avatar-crop-description"
      onCancel={event => { event.preventDefault(); if (!applying) setSource(null); }}>
      <div className="avatar-crop-dialog-heading"><h2 id="avatar-crop-title">Настроить фото</h2><button type="button" disabled={applying} aria-label="Закрыть настройку фото" onClick={() => setSource(null)}>×</button></div>
      <p id="avatar-crop-description">Перетащите фото, чтобы выбрать область. Используйте стрелки на клавиатуре для точной настройки.</p>
      {source && <div className="avatar-crop-stage" tabIndex={0} role="group" aria-label="Область кадрирования фото" aria-describedby="avatar-crop-description"
        onPointerDown={event => { if (applying || (event.pointerType === 'mouse' && event.button !== 0)) return; event.currentTarget.focus(); event.currentTarget.setPointerCapture(event.pointerId); drag.current = { x: event.clientX, y: event.clientY, position }; }}
        onPointerMove={move} onPointerUp={() => { drag.current = null; }} onPointerCancel={() => { drag.current = null; }} onLostPointerCapture={() => { drag.current = null; }}
        onKeyDown={event => {
          const steps: Record<string, Position> = { ArrowLeft: {x: -5, y: 0}, ArrowRight: {x: 5, y: 0}, ArrowUp: {x: 0, y: -5}, ArrowDown: {x: 0, y: 5} };
          const step = steps[event.key];
          if (step && !applying) { event.preventDefault(); setPosition(old => constrain({ x: old.x + step.x, y: old.y + step.y })); }
        }}>
        <img src={source.url} alt="Выбранное фото для кадрирования" draggable={false} style={{ width: `${width / SIZE * 100}%`, height: `${height / SIZE * 100}%`, left: `${50 + position.x / SIZE * 100}%`, top: `${50 + position.y / SIZE * 100}%` }}/>
        <div className="avatar-crop-mask" aria-hidden="true"/>
      </div>}
      <div className="avatar-zoom"><label htmlFor="avatar-zoom">Масштаб</label><button type="button" disabled={applying || zoom <= 1} aria-label="Уменьшить фото" onClick={() => changeZoom(zoom - 0.1)}>−</button>
        <input id="avatar-zoom" type="range" min={1} max={3} step={0.01} value={zoom} disabled={applying} onChange={event => changeZoom(Number(event.target.value))}/>
        <button type="button" disabled={applying || zoom >= 3} aria-label="Увеличить фото" onClick={() => changeZoom(zoom + 0.1)}>+</button></div>
      {cropError && <p className="error" role="alert">{cropError}</p>}
      <div className="avatar-crop-actions"><button type="button" disabled={applying} onClick={() => setSource(null)}>Отмена</button><button type="button" className="velo-button" disabled={applying || !source} onClick={apply}>{applying ? 'Обрабатываем…' : 'Применить'}</button></div>
    </dialog>
  </section>;
}
