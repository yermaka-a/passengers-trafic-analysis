import { markRaw } from "vue";
import { defineStore } from "pinia";
import * as L from "leaflet";
import { LeafletMapConfig } from "@/config";

interface MapStore {
  mapInstance: L.Map | null;
}

export const useMapStore = defineStore("mapstore", {
  state: (): MapStore => {
    return {
      mapInstance: null,
    };
  },
  getters: {
    getMapRef(state) {
      return state.mapInstance;
    },
  },
  actions: {
    initMap(id: string) {
      if (this.mapInstance) return; // Не создаем дубликат

      const instance = L.map(id, { zoomControl: false }).setView(
        LeafletMapConfig.startedCoords,
        LeafletMapConfig.startedZoom,
      );

      this.mapInstance = markRaw(instance);
    },
  },
});
