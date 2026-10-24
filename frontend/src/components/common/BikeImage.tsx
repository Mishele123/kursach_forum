import Landscape from './Landscape';
import type { Bike } from '../../types';
export default function BikeImage({ bike }: { bike: Bike }) { return <div aria-label={`${bike.brand} ${bike.model}`}><Landscape /></div>; }
