/**
 * Конфигурация Deck.gl
 *
 * Содержит настройки по умолчанию для слоёв и взаимодействия
 */

import type { DeckGLStyle } from "@/types";

export const DeckGLMapConfig = {
  // Начальное состояние вида (совпадает с LeafletMapConfig)
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
      color: [0, 128, 255, 180] as [number, number, number, number],
      strokeWidth: 3,
      filled: true,
      fillOpacity: 0.5,
    },
    Polyline: {
      color: [255, 0, 0, 255] as [number, number, number, number],
      strokeWidth: 5, // Увеличено с 3 до 5 для лучшей видимости
      filled: false,
      fillOpacity: 0,
    },
    CircleMarker: {
      color: [0, 255, 0, 255] as [number, number, number, number],
      strokeWidth: 2,
      filled: true,
      fillOpacity: 1,
      radiusMinPixels: 8,
      radiusMaxPixels: 20,
    },
  } as Record<string, DeckGLStyle>,

  // Настройки взаимодействия
  interaction: {
    pickable: true,
    autoHighlight: true,
    highlightColor: [255, 255, 0, 100] as [number, number, number, number],
  },

  // Настройки слоёв
  layers: {
    // Общий Z-index для Deck.gl overlay
    zIndex: 1000,
  },
};

export default DeckGLMapConfig;
