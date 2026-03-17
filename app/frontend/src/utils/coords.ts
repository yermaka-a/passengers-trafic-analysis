/**
 * Утилиты для конвертации координат между форматами
 *
 * MapLibre / Deck.gl / GeoJSON используют [lng, lat] (долгота, широта)
 * Бэкенд хранит { lat: number, lng: number }
 */

import type { LngLatTuple, BackendLatLng } from "@/types";

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
export const backendCoordToDeckGL = ({ lat, lng }: BackendLatLng): LngLatTuple => [
  lng,
  lat,
];

/**
 * Конвертирует одиночную координату из Deck.gl в Backend
 */
export const deckGLToBackendCoord = ([lng, lat]: LngLatTuple): BackendLatLng => ({
  lat,
  lng,
});

// ============================================================================
// АЛИАСЫ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ (удалить после рефакторинга)
// ============================================================================

export const backendCoordsToL7 = backendCoordsToDeckGL;
export const l7ToBackendCoords = deckGLToBackendCoords;
export const backendCoordToL7 = backendCoordToDeckGL;
export const l7ToBackendCoord = deckGLToBackendCoord;
