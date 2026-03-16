/**
 * Утилиты для конвертации координат между форматами
 *
 * MapLibre / L7 / GeoJSON используют [lng, lat] (долгота, широта)
 * Бэкенд хранит { lat: number, lng: number }
 */

import type { LngLatTuple, BackendLatLng } from "@/types";

/**
 * Конвертирует массив координат из бэкенда в L7 формат
 * Backend: [{lat, lng}, ...] → L7: [[lng, lat], ...]
 */
export const backendCoordsToL7 = (coords: BackendLatLng[]): LngLatTuple[] => {
  return coords.map(({ lat, lng }) => [lng, lat]);
};

/**
 * Конвертирует L7 координаты в формат для бэкенда
 * L7: [[lng, lat], ...] → Backend: [{lat, lng}, ...]
 */
export const l7ToBackendCoords = (coords: LngLatTuple[]): BackendLatLng[] => {
  return coords.map(([lng, lat]) => ({ lat, lng }));
};

/**
 * Конвертирует одиночную координату из Backend в L7
 */
export const backendCoordToL7 = ({ lat, lng }: BackendLatLng): LngLatTuple => [
  lng,
  lat,
];

/**
 * Конвертирует одиночную координату из L7 в Backend
 */
export const l7ToBackendCoord = ([lng, lat]: LngLatTuple): BackendLatLng => ({
  lat,
  lng,
});

// ============================================================================
// АЛИАСЫ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ (можно удалить после рефакторинга)
// ============================================================================

export const backendCoordsToDeckGL = backendCoordsToL7;
export const deckGLToBackendCoords = l7ToBackendCoords;
export const backendCoordToDeckGL = backendCoordToL7;
export const deckGLToBackendCoord = l7ToBackendCoord;
