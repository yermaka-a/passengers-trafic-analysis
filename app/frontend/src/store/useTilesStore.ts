import { defineStore } from "pinia";

export type TileLayer = "osm" | "satellite" | "hybrid" | "openfreemap" | "cartodb_positron" | "cartodb_dark";

export interface TileLayerConfig {
  name: string;
  tiles?: string[];
  style?: string; // Для векторных стилей
  attribution?: string;
  type?: "raster" | "vector";
}

export const useTilesStore = defineStore("tiles", {
  state: () => ({
    currentLayer: "osm" as TileLayer,
    layers: {
      osm: {
        name: "OSM",
        tiles: [
          "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
          "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
          "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
        ],
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        type: "raster" as const,
      },
      satellite: {
        name: "Satellite",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        ],
        attribution: "&copy; Esri",
        type: "raster" as const,
      },
      hybrid: {
        name: "Hybrid",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
          "https://stamen-tiles.a.ssl.fastly.net/toner-labels/{z}/{x}/{y}.png",
        ],
        attribution: "&copy; Esri, &copy; Stamen Design",
        type: "raster" as const,
      },
      openfreemap: {
        name: "OpenFreeMap (мультиязычный)",
        style: "https://tiles.openfreemap.org/styles/liberty",
        attribution: "© OpenFreeMap © OpenStreetMap",
        type: "vector" as const,
        note: "Названия на нескольких языках",
        license: "Бесплатно, без лимитов, коммерческое использование разрешено",
      },
      cartodb_positron: {
        name: "CartoDB Positron ⚠️",
        style: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        attribution: "© OpenStreetMap © CartoDB",
        type: "vector" as const,
        note: "Одноязычный (английский), только для некоммерческого использования!",
        license: "Бесплатно для некоммерческого, Enterprise для коммерческого",
      },
      cartodb_dark: {
        name: "CartoDB Dark Matter ⚠️",
        style: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        attribution: "© OpenStreetMap © CartoDB",
        type: "vector" as const,
        note: "Тёмная тема, только для некоммерческого использования!",
        license: "Бесплатно для некоммерческого, Enterprise для коммерческого",
      },
    } as Record<TileLayer, TileLayerConfig>,
  }),
  actions: {
    setLayer(layer: TileLayer) {
      this.currentLayer = layer;
      // Сохраняем в localStorage для синхронизации
      localStorage.setItem('currentTileLayer', layer);
    },
    getCurrentLayerConfig(): TileLayerConfig {
      return this.layers[this.currentLayer];
    },
    loadFromStorage() {
      const saved = localStorage.getItem('currentTileLayer');
      if (saved && ['osm', 'satellite', 'hybrid', 'openfreemap', 'cartodb_positron', 'cartodb_dark'].includes(saved)) {
        this.currentLayer = saved as TileLayer;
      }
    },
  },
});
