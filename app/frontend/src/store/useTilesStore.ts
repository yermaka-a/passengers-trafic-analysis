import { defineStore } from "pinia";

export type TileLayer = "osm" | "satellite" | "hybrid";

export interface TileLayerConfig {
  name: string;
  tiles: string[];
  attribution: string;
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
      },
      satellite: {
        name: "Satellite",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        ],
        attribution: "&copy; Esri",
      },
      hybrid: {
        name: "Hybrid",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
          "https://stamen-tiles.a.ssl.fastly.net/toner-labels/{z}/{x}/{y}.png",
        ],
        attribution: "&copy; Esri, &copy; Stamen Design",
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
      if (saved && ['osm', 'satellite', 'hybrid'].includes(saved)) {
        this.currentLayer = saved as TileLayer;
      }
    },
  },
});
