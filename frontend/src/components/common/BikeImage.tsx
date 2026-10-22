import { useState } from 'react';
import type { Bike } from '../../types';
import Landscape from './Landscape';

export default function BikeImage({ bike }: { bike: Bike }) {
  const [failedUrl, setFailedUrl] = useState<string | null>(null);
  return bike.photo_url && bike.photo_url !== failedUrl
    ? <img className="bike-photo" src={bike.photo_url} alt={`${bike.brand} ${bike.model}`} onError={() => setFailedUrl(bike.photo_url || null)} />
    : <Landscape />;
}
