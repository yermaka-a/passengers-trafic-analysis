/**
 * Утилиты для конвертации координат между форматами
 * 
 * Leaflet использует [lat, lng] (широта, долгота)
 * Deck.gl / GeoJSON используют [lng, lat] (долгота, широта)
 * Бэкенд хранит { lat: number, lng: number }
 */

import type { LatLngTuple, LngLatTuple, BackendLatLng } from '@/types';

/**
 * Конвертирует Leaflet [lat, lng] → Deck.gl [lng, lat]
 */
export const leafletToDeckGL = ([lat, lng]: LatLngTuple): LngLatTuple => [lng, lat];

/**
 * Конвертирует Deck.gl [lng, lat] → Leaflet [lat, lng]
 */
export const deckGLToLeaflet = ([lng, lat]: LngLatTuple): LatLngTuple => [lat, lng];

/**
 * Конвертирует массив координат из бэкенда в Deck.gl формат
 * Backend: [{lat, lng}, ...] → Deck.gl: [[lng, lat], ...]
 */
export const backendCoordsToDeckGL = (coords: BackendLatLng[]): LngLatTuple[] => {
  return coords.map(({ lat, lng }) => [lng, lat]);
};

/**
 * Конвертирует Deck.gl координаты в формат для бэкенда
 * Deck.gl: [[lng, lat], ...] → Backend: [{lat, lng}, ...]
 */
export const deckGLToBackendCoords = (coords: LngLatTuple[]): BackendLatLng[] => {
  return coords.map(([lng, lat]) => ({ lat, lng }));
};

/**
 * Конвертирует одиночную координату из Backend в Deck.gl
 */
export const backendCoordToDeckGL = ({ lat, lng }: BackendLatLng): LngLatTuple => [lng, lat];

/**
 * Конвертирует одиночную координату из Deck.gl в Backend
 */
export const deckGLToBackendCoord = ([lng, lat]: LngLatTuple): BackendLatLng => ({ lat, lng });
