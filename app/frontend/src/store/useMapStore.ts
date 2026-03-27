import { ref, reactive } from "vue";
import { defineStore } from "pinia";
import { Map, NavigationControl, AttributionControl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { MaplibreMapConfig } from "@/config/MaplibreMapConfig";

export const useMapStore = defineStore("mapstore", () => {
  const mapInstance = ref<Map | null>(null);
  const viewState = reactive({
    latitude: MaplibreMapConfig.initialViewState.center[1]!,
    longitude: MaplibreMapConfig.initialViewState.center[0]!,
    zoom: MaplibreMapConfig.initialViewState.zoom,
    pitch: MaplibreMapConfig.initialViewState.pitch,
    bearing: MaplibreMapConfig.initialViewState.bearing,
  });
  
  // Функция для открытия popup (будет установлена из Map.vue)
  const showObjectPopup = ref<(id: string) => void | null>(null);

  function initMap(containerId: string) {
    if (mapInstance.value) return;

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

    mapInstance.value = instance;
  }

  function updateViewState(updates: Partial<typeof viewState>) {
    Object.assign(viewState, updates);

    if (mapInstance.value) {
      const { latitude, longitude, zoom, pitch, bearing } = viewState;
      mapInstance.value.easeTo({
        center: [longitude, latitude],
        zoom,
        pitch,
        bearing,
        duration: 500,
      });
    }
  }

  // Метод для открытия popup из других компонентов
  const openPopup = (id: string) => {
    if (showObjectPopup.value) {
      showObjectPopup.value(id);
    }
  };

  return {
    mapInstance,
    viewState,
    showObjectPopup,
    openPopup,
    initMap,
    updateViewState,
  };
});
