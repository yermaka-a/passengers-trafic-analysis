/**
 * Конфигурация AntV L7
 *
 * Заменяет DeckGLMapConfig
 */

import type { L7Style } from "@/types";

export const L7MapConfig = {
  // Начальное состояние вида (совпадает с MaplibreMapConfig)
  initialViewState: {
    latitude: 52.544358,
    longitude: 103.888249,
    zoom: 14,
    pitch: 0,
    bearing: 0,
  },

  // Стили слоёв по умолчанию
  defaultStyles: {
    Polygon: {
      fillColor: [0, 128, 255, 180] as [number, number, number, number],
      strokeColor: [0, 128, 255, 255] as [number, number, number, number],
      strokeWidth: 3,
      filled: true,
      fillOpacity: 0.5,
    },
    Polyline: {
      strokeColor: [255, 0, 0, 255] as [number, number, number, number],
      strokeWidth: 5,
    },
    CircleMarker: {
      fillColor: [0, 255, 0, 255] as [number, number, number, number],
      strokeColor: [0, 255, 0, 255] as [number, number, number, number],
      strokeWidth: 2,
      radius: 10,
    },
  } as Record<string, L7Style>,

  // Настройки взаимодействия
  interaction: {
    enableHighlight: true,
    highlightColor: [255, 255, 0, 100] as [number, number, number, number],
  },

  // Настройки сцены
  scene: {
    logo: false,
    mapControl: false,
    zoomControl: false,
  },
};

export default L7MapConfig;
