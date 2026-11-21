import { useEffect, useRef } from 'react';
import { control, divIcon, map, marker as createMarker, tileLayer } from 'leaflet';
import type { LatLng, Marker, Map as LeafletMap } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { PostPlace } from '../../types';

export type MapPoint = Pick<PostPlace, 'latitude' | 'longitude'>;

function toPoint(coordinates: LatLng): MapPoint {
  const { lat, lng } = coordinates.wrap();
  return { latitude: Number(lat.toFixed(6)), longitude: Number(lng.toFixed(6)) };
}

export default function LocationMap({ point, onPick }: {
  point: MapPoint | null;
  onPick?: (point: MapPoint) => void;
}) {
  const container = useRef<HTMLDivElement>(null);
  const instance = useRef<LeafletMap | null>(null);
  const marker = useRef<Marker | null>(null);
  const initial = useRef(point).current;

  useEffect(() => {
    if (!container.current) return;
    const view = map(container.current, {
      zoomControl: false,
      scrollWheelZoom: false,
      dragging: !!onPick,
      touchZoom: !!onPick,
      doubleClickZoom: false,
      boxZoom: false,
      keyboard: !!onPick,
    }).setView(initial ? [initial.latitude, initial.longitude] : [53.1959, 50.1002], initial ? 15 : 12);
    instance.current = view;
    view.attributionControl.setPrefix(false);
    tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      noWrap: true,
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(view);

    if (onPick) {
      control.zoom({ position: 'topright', zoomInTitle: 'Приблизить', zoomOutTitle: 'Отдалить' }).addTo(view);
      view.on('click', event => onPick(toPoint(event.latlng)));
    }

    return () => {
      view.remove();
      instance.current = null;
      marker.current = null;
    };
  }, [initial, onPick]);

  useEffect(() => {
    const view = instance.current;
    if (!point || !view) return;
    const latLng: [number, number] = [point.latitude, point.longitude];
    if (marker.current) {
      marker.current.setLatLng(latLng);
    } else {
      marker.current = createMarker(latLng, {
        icon: divIcon({ className: 'post-map-pin', iconSize: [24, 24], iconAnchor: [12, 23] }),
        interactive: false, keyboard: false,
      }).addTo(view);
    }
    if (!onPick) view.setView(latLng, 15, { animate: false });
  }, [point, onPick]);

  return <div ref={container} className="post-location-map" role="region" aria-label="Карта"
    onKeyDown={event => {
      if (event.key === 'Enter' && event.target === event.currentTarget && onPick && instance.current) {
        event.preventDefault();
        onPick(toPoint(instance.current.getCenter()));
      }
    }} />;
}
