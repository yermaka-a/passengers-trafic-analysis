import "leaflet";
import type { ObjTypes, ObjNames } from "@/store/useMapObjectStore";

// ============================================================================
// РАСШИРЕНИЕ ТИПОВ LEAFLET (для обратной совместимости)
// ============================================================================

declare module "leaflet" {
  interface PolylineOptions {
    Id: string;
    name: ObjNames;
    objType: Exclude<ObjTypes, "Edit">;
    CustomName?: string;
    description?: string;
  }
  interface CircleMarkerOptions {
    Id: string;
    name: ObjNames;
    objType: Exclude<ObjTypes, "Edit">;
    CustomName?: string;
    description?: string;
  }
}

import * as L from "leaflet";

// ============================================================================
// ТИПЫ ДЛЯ БЭКЕНДА (точно соответствуют Pydantic схемам)
// ============================================================================

/** Координата в формате бэкенда (Leaflet) */
export interface BackendLatLng {
  lat: number;
  lng: number;
}

/** Опции объекта (точно как Options в Pydantic) */
export interface BackendObjectOptions {
  Id: string;
  name: string;
  description?: string | null;
  customName?: string | null;
  color?: string | null;
  stroke?: boolean | null;
  weight?: number | null;
  fill?: boolean | null;
  fillOpacity?: number | null;
  objType: Exclude<ObjTypes, "Edit">;
  dashArray?: number[] | null;
}

/** Объект для отправки на бэкенд */
export interface BackendObjectCreate {
  latlng: BackendLatLng[];
  options: BackendObjectOptions;
}

/** Ответ от бэкенда (упрощённый) */
export interface BackendResponse {
  status: "success" | "failed";
  message?: string;
  obj?: BackendObjectCreate;
  objects?: BackendObjectCreate[];
}

// ============================================================================
// ТИПЫ ДЛЯ DECK.GL
// ============================================================================

export type LatLngTuple = [number, number]; // [lat, lng] - Leaflet формат
export type LngLatTuple = [number, number]; // [lng, lat] - Deck.gl / GeoJSON формат

export interface DeckGLStyle {
  color: [number, number, number, number]; // RGBA [0-255]
  strokeWidth: number;
  strokeDasharray?: [number, number];
  filled: boolean;
  fillOpacity: number;
}

/** Объект Deck.gl для отображения на карте */
export interface DeckGLObject {
  id: string;
  type: Exclude<ObjTypes, "Edit">;
  name: string;
  customName?: string;
  description?: string;
  style: DeckGLStyle;
  // Координаты в формате Deck.gl [lng, lat]
  coordinates: LngLatTuple[];
}

// ============================================================================
// СУЩЕСТВУЮЩИЙ ТИП (для обратной совместимости)
// ============================================================================

export interface ObjectCreate {
  latlng: L.LatLng[];
  options: L.PolylineOptions | L.CircleMarkerOptions;
}
