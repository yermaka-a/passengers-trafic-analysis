import { markRaw } from "vue";
import { defineStore } from "pinia";
import * as L from "leaflet";
import { LeafletMapConfig } from "@/config";

interface MapStore {
  mapInstance: L.Map | null;
  viewState: {
    latitude: number;
    longitude: number;
    zoom: number;
  };
}

export const useMapStore = defineStore("mapstore", {
  state: (): MapStore => {
    return {
      mapInstance: null,
      viewState: {
        latitude: LeafletMapConfig.startedCoords[0],
        longitude: LeafletMapConfig.startedCoords[1],
        zoom: LeafletMapConfig.startedZoom,
      },
    };
  },
  getters: {
    getMapRef(state) {
      return state.mapInstance;
    },
    getViewState(state) {
      return state.viewState;
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
    updateViewState(updates: Partial<typeof this.viewState>) {
      this.viewState = { ...this.viewState, ...updates };

      // Если карта существует, обновляем и её
      if (this.mapInstance) {
        this.mapInstance.setView(
          [this.viewState.latitude, this.viewState.longitude],
          this.viewState.zoom,
        );
      }
    },
  },
});
