import type { ObjTypes, ObjNames } from "@/store/useMapObjectStore";
import type { Map } from "maplibre-gl";

// ============================================================================
// ТИПЫ ДЛЯ БЭКЕНДА (точно соответствуют Pydantic схемам)
// ============================================================================

/** Координата в формате бэкенда */
export interface BackendLatLng {
  lat: number;
  lng: number;
}

/** Опции объекта */
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

/** Ответ от бэкенда */
export interface BackendResponse {
  status: "success" | "failed";
  message?: string;
  obj?: BackendObjectCreate;
  objects?: BackendObjectCreate[];
}

// ============================================================================
// ТИПЫ ДЛЯ ANTВ L7
// ============================================================================

/** Координата в формате L7: [lng, lat] (GeoJSON standard) */
export type LngLatTuple = [number, number];

/** Стиль L7 объекта */
export interface L7Style {
  fillColor?: [number, number, number, number]; // RGBA
  strokeColor?: [number, number, number, number];
  strokeWidth?: number;
  strokeDasharray?: [number, number];
  filled?: boolean;
  fillOpacity?: number;
  radius?: number; // для CircleMarker
}

/** Объект L7 для отображения на карте */
export interface L7Object {
  id: string;
  type: Exclude<ObjTypes, "Edit">;
  name: string;
  customName?: string;
  description?: string;
  style: L7Style;
  coordinates: LngLatTuple[]; // [lng, lat]
}

// ============================================================================
// УДАЛЕНО: Leaflet и Deck.gl типы больше не нужны
// ============================================================================
