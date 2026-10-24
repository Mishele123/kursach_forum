import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useBikes } from '../hooks';
import { bikesApi, errorMessage } from '../services/api';
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
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(''); setBusy(true);
    const data = new FormData(event.currentTarget);
    try {
      const brand = String(data.get('brand')).trim();
      const model = String(data.get('model')).trim();
      if (!brand || !model) { setError('Введите бренд и модель велосипеда'); return; }
      await bikesApi.createBike({ brand, model, year: Number(data.get('year')) });
      navigate('/bikes');
    } catch (err) { setError(errorMessage(err)); } finally { setBusy(false); }
  }
  return <section className="velo-page"><h1>Добавить велосипед</h1><p className="subtitle">Расскажите сообществу, на чём вы катаетесь</p>
    <form className="velo-card velo-form" onSubmit={submit}>
      {error && <p role="alert" className="error">{error}</p>}
      <fieldset className="profile-fields" disabled={busy}>
      <Input label="Бренд *" name="brand" placeholder="Trek" required maxLength={100} />
      <Input label="Модель *" name="model" placeholder="Marlin 7" required maxLength={100} />
      <Input label="Год выпуска *" name="year" type="number" min={1800} max={Math.min(2200, new Date().getFullYear() + 1)} placeholder="2023" required />
      </fieldset>
      <p className="subtitle">* Обязательные поля</p><div className="form-actions"><Button type="submit" isLoading={busy}>Добавить велосипед</Button><Link className="velo-button secondary" to="/bikes">Отмена</Link></div>
    </form></section>;
}
