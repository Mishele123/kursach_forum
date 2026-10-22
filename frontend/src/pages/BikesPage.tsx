import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useBikes } from '../hooks';
import { bikesApi, errorMessage, uploadPhoto } from '../services/api';
import { Button, Input, Loading } from '../components/common';
import BikeImage from '../components/common/BikeImage';
export function BikesPage() {
  const { bikes, isLoading, error, refetch } = useBikes();
  return <section className="velo-page"><h1>Мои велосипеды</h1><p className="subtitle">Ваш гараж. У каждого велосипеда своя история.</p>
    <Link className="velo-button" to="/bikes/add">+ Добавить велосипед</Link>
    {isLoading ? <Loading /> : error ? <div role="alert">{error}<button onClick={refetch}>Повторить</button></div> :
      <div className="bike-grid">{bikes.map(bike => <article className="velo-card" key={bike.id}><BikeImage bike={bike} /><h2>{bike.brand} {bike.model}</h2><p>{bike.year} · Год выпуска</p></article>)}
        {!bikes.length && <div className="velo-card"><h2>Всё начинается с велосипеда.</h2><p>Добавьте свой первый байк в гараж.</p></div>}</div>}
  </section>;
}
export function AddBikePage() {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoUrl, setPhotoUrl] = useState<string | undefined>();
  const [preview, setPreview] = useState('');
  const fileInput = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (!photo) { setPreview(''); return; }
    const url = URL.createObjectURL(photo); setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [photo]);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(''); setBusy(true);
    const data = new FormData(event.currentTarget);
    try {
      const brand = String(data.get('brand')).trim();
      const model = String(data.get('model')).trim();
      if (!brand || !model) { setError('Введите бренд и модель велосипеда'); return; }
      const photo_url = photo ? await uploadPhoto(photo) : photoUrl;
      if (photo) { setPhotoUrl(photo_url); setPhoto(null); }
      await bikesApi.createBike({ brand, model, year: Number(data.get('year')), photo_url });
      navigate('/bikes');
    } catch (err) { setError(errorMessage(err)); } finally { setBusy(false); }
  }
  return <section className="velo-page"><h1>Добавить велосипед</h1><p className="subtitle">Расскажите сообществу, на чём вы катаетесь</p>
    <form className="velo-card velo-form" onSubmit={submit}>
      {error && <p role="alert" className="error">{error}</p>}
      <fieldset className="profile-fields" disabled={busy}>
      <Input label="Бренд *" name="brand" placeholder="Trek" required maxLength={100} />
      <Input label="Модель *" name="model" placeholder="Marlin 7" required maxLength={100} />
      <Input label="Год выпуска *" name="year" type="number" min={1800} max={new Date().getFullYear() + 1} placeholder="2023" required />
      <div className="upload-area">
        <label htmlFor="bike-photo">Фото велосипеда</label>
        <p>Необязательно · JPG, PNG, GIF, WEBP · до 5 МБ</p>
        <input ref={fileInput} id="bike-photo" type="file" accept="image/jpeg,image/png,image/gif,image/webp" onChange={event => {
          const file = event.target.files?.[0] || null;
          if (file && (file.size > 5*1024*1024 || !['image/jpeg','image/png','image/gif','image/webp'].includes(file.type))) {
            setError('Выберите JPG, PNG, GIF или WEBP размером до 5 МБ'); event.target.value = ''; setPhoto(null); setPhotoUrl(undefined); return;
          }
          setError(''); setPhoto(file); setPhotoUrl(undefined);
        }} />
        {(preview || photoUrl) && <><img className="upload-preview" src={preview || photoUrl} alt="Предпросмотр велосипеда" />
          <button type="button" onClick={() => { setPhoto(null); setPhotoUrl(undefined); if (fileInput.current) fileInput.current.value = ''; }}>Убрать фотографию</button></>}
      </div>
      </fieldset>
      <p className="subtitle">* Обязательные поля</p><div className="form-actions"><Button type="submit" isLoading={busy}>Добавить велосипед</Button><Link className="velo-button secondary" to="/bikes">Отмена</Link></div>
    </form></section>;
}
