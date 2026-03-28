/**
 * Конфигурация MapLibre GL JS
 *
 * Заменяет LeafletMapConfig
 */

import type { StyleSpecification } from "maplibre-gl";

export const MaplibreMapConfig = {
  // Начальное состояние вида (совпадает с LeafletMapConfig)
  initialViewState: {
    center: [103.888249, 52.544358] as [number, number], // [lng, lat]
    zoom: 14,
    pitch: 0,
    bearing: 0,
  },

  // Стиль карты (OSM raster tiles)
  style: {
    version: 8,
    sources: {
      "osm": {
        type: "raster",
        tiles: [
          "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
          "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
          "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
        ],
        tileSize: 256,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      },
    },
    layers: [
      {
        id: "osm-layer",
        type: "raster",
        source: "osm",
      },
    ],
  } as StyleSpecification,

  // Настройки взаимодействия
  interaction: {
    scrollZoom: true,
    dragPan: true,
    dragRotate: false, // 2D режим
    pitchWithRotate: false,
    doubleClickZoom: true,
    touchZoomRotate: false,
  },

  // Контролы
  controls: {
    attribution: true,
    logo: false,
    navigation: true, // zoom кнопки
    geolocate: false,
  },
};

export default MaplibreMapConfig;
