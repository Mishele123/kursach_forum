import {useState} from 'react';
import {mediaUrl} from '../../services/api';
import type {Bike} from '../../types';
export default function BikeImage({bike}: {bike: Bike}) {
 const [failed,setFailed]=useState<string|null>(null);
 return bike.photo_url && failed!==bike.photo_url ? <img className="bike-photo" src={mediaUrl(bike.photo_url)} alt={`${bike.brand} ${bike.model}`} onError={()=>setFailed(bike.photo_url)}/> : <div className="bike-no-photo" role="img" aria-label={`${bike.brand} ${bike.model} — пока нет фото`}><svg viewBox="0 0 96 64" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="22" cy="43" r="16"/><circle cx="75" cy="43" r="16"/><path d="m22 43 18-29 14 29H22l15-23h27l11 23M54 43 67 8h-9M33 12h14M64 8h9q6 0 6 5"/></svg><span>Пока нет фото</span></div>;
}
