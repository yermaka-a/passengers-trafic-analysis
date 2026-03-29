import type { ObjTypes, ObjNames } from "@/store/useMapObjectStore";
import type { StopMarkerType } from "@/config/stopMarkers";
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
  objType: Exclude<ObjTypes, "Edit"> | "StopMarker";
  dashArray?: number[] | null;
  markerType?: string | null; // Для StopMarker
  radius?: number | null; // Для StopMarker/CircleMarker
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
// ТИПЫ ДЛЯ DECK.GL
// ============================================================================

/** Координата в формате Deck.gl: [lng, lat] (GeoJSON standard) */
export type LngLatTuple = [number, number];

/** Стиль Deck.gl объекта */
export interface DeckGLStyle {
  color: [number, number, number, number]; // RGBA
  strokeWidth?: number;
  strokeDasharray?: [number, number];
  filled?: boolean;
  fillOpacity?: number;
  radius?: number; // для CircleMarker
  getSizeScale?: number; // для StopMarker (IconLayer)
}

/** Объект Deck.gl для отображения на карте */
export interface DeckGLObject {
  id: string;
  type: Exclude<ObjTypes, "Edit"> | "StopMarker";
  name: string;
  customName?: string | null;
  description?: string | null;
  style: DeckGLStyle;
  coordinates: LngLatTuple[]; // [lng, lat]
  // Для StopMarker
  markerType?: StopMarkerType;
  iconData?: {
    id: StopMarkerType;
    svg: string;
    width: number;
    height: number;
  };
}

// ============================================================================
// УДАЛЕНО: L7 типы больше не нужны
// ============================================================================
