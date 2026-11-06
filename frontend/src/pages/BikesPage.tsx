import GarageBikeCard from '../components/GarageBikeCard';
import PhotoPicker from '../components/common/PhotoPicker';
import { useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useBikes } from '../hooks';
import { bikesApi, errorMessage } from '../services/api';
import { Button, Input, Loading } from '../components/common';

export function BikesPage() {
  const { bikes, isLoading, error, refetch } = useBikes();
  return <section className="velo-page garage-page">
    <header className="garage-page-heading"><div><h1>Мои велосипеды{!isLoading && !error && <span className="profile-count">{bikes.length}</span>}</h1><p className="subtitle">Ваш гараж. У каждого велосипеда своя история.</p></div><Link className="velo-button" to="/bikes/add">+ Добавить велосипед</Link></header>
    {isLoading ? <Loading /> : error ? <div className="velo-card error" role="alert"><p>{error}</p><button type="button" className="velo-button secondary" onClick={refetch}>Повторить</button></div> : bikes.length > 0 ? <><div className="garage-bikes-grid">{bikes.map(bike => <GarageBikeCard key={bike.id} bike={bike} onSaved={refetch} />)}</div><p className="garage-photo-help">Фотография поможет быстрее узнать велосипед в вашем гараже.</p></> : <div className="velo-card garage-empty"><h2>Всё начинается с велосипеда.</h2><p>Добавьте свой первый байк в гараж. Фотографию можно загрузить позже.</p><Link className="velo-button secondary" to="/bikes/add">Добавить первый велосипед</Link></div>}
  </section>;
}
export function AddBikePage() {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [photos, setPhotos] = useState<File[]>([]);
  const [createdId, setCreatedId] = useState<number | null>(null);
  const pending = useRef(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending.current) return;
    pending.current = true; setError(''); setBusy(true);
    const data = new FormData(event.currentTarget);
    try {
      const brand = String(data.get('brand')).trim();
      const model = String(data.get('model')).trim();
      if (createdId === null && (!brand || !model)) { setError('Введите бренд и модель велосипеда'); return; }
      const bikeId = createdId ?? (await bikesApi.createBike({ brand, model, year: Number(data.get('year')) })).id;
      setCreatedId(bikeId);
      if (photos.length) await bikesApi.uploadPhoto(bikeId, photos[0]);
      navigate('/bikes');
    } catch (err) { setError(errorMessage(err)); } finally { pending.current = false; setBusy(false); }
  }
  return <section className="velo-page"><h1>Добавить велосипед</h1><p className="subtitle">Расскажите сообществу, на чём вы катаетесь</p>
    <form className="velo-card velo-form" onSubmit={submit}>
      {error && <p role="alert" className="error">{error}</p>}
      <fieldset className="profile-fields" disabled={busy || createdId !== null}>
      <Input label="Бренд *" name="brand" placeholder="Trek" required maxLength={100} />
      <Input label="Модель *" name="model" placeholder="Marlin 7" required maxLength={100} />
      <Input label="Год выпуска *" name="year" type="number" min={1800} max={Math.min(2200, new Date().getFullYear() + 1)} placeholder="2023" required />
      </fieldset>
      <PhotoPicker files={photos} onChange={setPhotos} disabled={busy} maximum={1}/>
      {createdId !== null && <p role="status">Велосипед уже сохранён. Повторите загрузку фото или <Link to="/bikes">перейдите в гараж</Link>. Можно убрать фото и продолжить без него.</p>}
      <p className="subtitle">* Обязательные поля. Фотографию можно добавить сейчас или позже.</p><div className="form-actions"><Button type="submit" isLoading={busy}>{createdId !== null ? (photos.length ? "Повторить загрузку фото" : "Продолжить без фото") : "Добавить велосипед"}</Button><Link className="velo-button secondary" to="/bikes">Отмена</Link></div>
    </form></section>;
}
