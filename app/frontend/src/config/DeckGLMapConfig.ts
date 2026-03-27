/**
 * Конфигурация Deck.gl
 *
 * Стили слоёв по умолчанию и настройки взаимодействия
 */

import type { DeckGLStyle } from "@/types";

export const DeckGLMapConfig = {
  // Начальное состояние вида (совпадает с MaplibreMapConfig)
  initialViewState: {
    longitude: 103.888249,
    latitude: 52.544358,
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
      strokeWidth: 5,
      filled: false,  // Добавляем заливку для полилайнов
      fillOpacity: 0.2,
    },
    CircleMarker: {
      color: [0, 255, 0, 255] as [number, number, number, number],
      radius: 10,
    },
  } as Record<string, DeckGLStyle>,

  // Настройки взаимодействия
  interaction: {
    autoHighlight: true,
    highlightColor: [255, 255, 0, 100] as [number, number, number, number],
    pickingRadius: 5, // Радиус для кликов
  },

  // Настройки рендеринга
  rendering: {
    devicePixels: true, // Использовать native resolution
  },
};

export default DeckGLMapConfig;
