import { markRaw } from "vue";
import { defineStore } from "pinia";
import { Map, NavigationControl, AttributionControl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { MaplibreMapConfig } from "@/config/MaplibreMapConfig";

interface MapStore {
  mapInstance: Map | null;
  viewState: {
    latitude: number;
    longitude: number;
    zoom: number;
    pitch: number;
    bearing: number;
  };
}

export const useMapStore = defineStore("mapstore", {
  state: (): MapStore => {
    return {
      mapInstance: null,
      viewState: {
        latitude: MaplibreMapConfig.initialViewState.center[1]!,
        longitude: MaplibreMapConfig.initialViewState.center[0]!,
        zoom: MaplibreMapConfig.initialViewState.zoom,
        pitch: MaplibreMapConfig.initialViewState.pitch,
        bearing: MaplibreMapConfig.initialViewState.bearing,
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
    initMap(containerId: string) {
      if (this.mapInstance) return;

      const instance = new Map({
        container: containerId,
        style: MaplibreMapConfig.style,
        center: MaplibreMapConfig.initialViewState.center,
        zoom: MaplibreMapConfig.initialViewState.zoom,
        pitch: MaplibreMapConfig.initialViewState.pitch,
        bearing: MaplibreMapConfig.initialViewState.bearing,
        ...MaplibreMapConfig.interaction,
      });

      // Добавляем контролы
      if (MaplibreMapConfig.controls.navigation) {
        instance.addControl(new NavigationControl());
      }
      if (MaplibreMapConfig.controls.attribution) {
        instance.addControl(new AttributionControl());
      }

      this.mapInstance = markRaw(instance);
    },
    updateViewState(updates: Partial<typeof this.viewState>) {
      this.viewState = { ...this.viewState, ...updates };

      if (this.mapInstance) {
        const { latitude, longitude, zoom, pitch, bearing } = this.viewState;
        this.mapInstance.easeTo({
          center: [longitude, latitude],
          zoom,
          pitch,
          bearing,
          duration: 500,
        });
      }
    },
  },
});
