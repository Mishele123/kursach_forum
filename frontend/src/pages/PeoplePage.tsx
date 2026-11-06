import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { peopleApi, errorMessage } from '../services/api';
import AvatarImage from '../components/common/AvatarImage';
import { Input } from '../components/common';
import type { PublicUser, PeopleFilters } from '../types';
const fields = ['city', 'discipline', 'brand', 'model'] as const;
export default function PeoplePage() {
  const [params] = useSearchParams();
  return <PeopleResults key={params.toString()} />;
}
function PeopleResults() {
  const [params, setParams] = useSearchParams();
  const filters: PeopleFilters = Object.fromEntries(fields.map(key => [key, params.get(key) || undefined]));
  const [items, setItems] = useState<PublicUser[]>([]);
  const [cursor, setCursor] = useState<number>();
  const [next, setNext] = useState<number | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  const query = params.toString();
  useEffect(() => {
    let active = true;
    setBusy(true); setError('');
    void peopleApi.search(filters, cursor).then(page => {
      if (!active) return;
      setItems(old => cursor !== undefined ? [...old, ...page.items.filter(person => !old.some(user => user.id === person.id))] : page.items);
      setNext(page.next_cursor);
    }).catch(err => { if (active) setError(errorMessage(err)); })
      .finally(() => { if (active) setBusy(false); });
    return () => { active = false; };
  }, [query, cursor, retry]);
  function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const updated = Object.fromEntries(fields.map(key => [key, String(data.get(key) || '').trim()]).filter(([, value]) => value));
    if (new URLSearchParams(updated).toString() === query) { setCursor(undefined); setRetry(value => value + 1); }
    else setParams(updated);
  }
  return <section className="velo-page people-page">
    <header className="people-heading"><h1>Найдите своих людей</h1><p className="subtitle">Велосипедисты рядом и владельцы похожих велосипедов</p></header>
    <form className="velo-card velo-form people-filters" onSubmit={search}>
      <div className="filter-grid"><Input name="city" label="Город" placeholder="Например, Самара" defaultValue={params.get('city') || ''} maxLength={100} /><Input name="discipline" label="Дисциплина" placeholder="Например, гравел" defaultValue={params.get('discipline') || ''} maxLength={100} /></div>
      <details className="people-bike-filters" open><summary>По велосипеду</summary><div className="filter-grid"><Input name="brand" label="Бренд" placeholder="Например, Trek" defaultValue={params.get('brand') || ''} maxLength={100} /><Input name="model" label="Модель" placeholder="Например, Marlin" defaultValue={params.get('model') || ''} maxLength={100} /></div></details>
      <div className="people-filter-actions"><button className="velo-button" type="submit">Найти людей</button><button type="button" className="people-reset" onClick={event => { event.currentTarget.form?.reset(); if (!query) { setCursor(undefined); setRetry(value => value + 1); } else setParams({}); }}>Сбросить</button></div>
    </form>
    <div className="people-results-heading"><h2>Участники сообщества</h2><span role="status">{busy ? 'Ищем людей…' : error ? '' : `Показано участников: ${items.length}`}</span></div>
    {error && <div className="error" role="alert"><p>{error}</p><button type="button" className="velo-button secondary" onClick={() => setRetry(value => value + 1)}>Повторить</button></div>}
    <div className="people-grid" aria-busy={busy}>{items.map(person => <Link className="velo-card person-card people-person" key={person.id} to={`/users/${person.id}`}>
      <div className="person-overview"><div className="avatar"><AvatarImage username={person.username} url={person.avatar_url} /></div><div className="person-information"><h2>{person.username}</h2><p>{[person.city, person.discipline].filter(Boolean).join(' · ') || 'Велосипедист сообщества'}</p>{person.interests.length > 0 && <ul className="person-interest-tags">{person.interests.slice(0, 3).map((interest, index) => <li key={`${interest}-${index}`}>{interest}</li>)}{person.interests.length > 3 && <li>+{person.interests.length - 3}</li>}</ul>}</div></div>
      <span className="person-open">Открыть профиль <span aria-hidden="true">→</span></span>
    </Link>)}</div>
    {!busy && !error && !items.length && <div className="velo-card people-empty"><h2>Пока никого не нашли</h2><p>Попробуйте изменить город, дисциплину или фильтры велосипеда.</p></div>}
    {next !== null && !error && <button className="velo-button people-load-more" disabled={busy} onClick={() => { if (next !== null) { setBusy(true); setCursor(next); } }}>Показать ещё</button>}
  </section>;
}
