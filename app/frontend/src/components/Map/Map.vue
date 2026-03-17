<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl from "maplibre-gl";
import { storeToRefs } from "pinia";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { useL7 } from "@/composables/useL7";
import { TilesSwitcher } from "@/components/TilesSwitcher";
import MapOptions from "./MapOptions.vue";
import PlusCursor from "@/assets/plus-cursor.svg";
import GrabCursor from "@/assets/grab-cursor.svg";
import type { LngLatTuple, DeckGLObject } from "@/types";

// Deck.gl imports
import { MapboxOverlay } from "@deck.gl/mapbox";
import { PolygonLayer, PathLayer, ScatterplotLayer } from "@deck.gl/layers";
import { DeckGLMapConfig } from "@/config/DeckGLMapConfig";

const mapObjectStore = useMapObjectStore();

const { Objects, DraftObject } = storeToRefs(mapObjectStore);

// MapLibre instance
const mapInstance = ref<maplibregl.Map | null>(null);

// Deck.gl overlay
let deckOverlay: MapboxOverlay | null = null;

// Курсоры
const plusCursor = computed(() => `url("${PlusCursor}") 16 16, auto`);
const grabCursor = computed(() => `url("${GrabCursor}") 16 16, auto`);

// Состояние для курсора
const isDragging = ref(false);

// L7 composable (переименовать потом в useDeckGL)
const {
  handleMapClick,
  finalizeObject,
  cancelObject,
  undo,
  redo,
  canUndo,
  canRedo,
} = useL7();

// Обработка клика по карте
const onMapClick = (e: any) => {
  const lngLat: LngLatTuple = [e.lngLat.lng, e.lngLat.lat];
  console.log("[Map] Клик:", lngLat);
  handleMapClick(lngLat);
};

// Выделение объекта при клике
const selectObject = (id: string) => {
  console.log("[Map] Select object:", id);
  mapObjectStore.ClickedObjId = id;
};

// Создание слоёв Deck.gl
const createDeckLayers = () => {
  const layers: any[] = [];
  
  const objectsArray = Array.from(Objects.value?.values() ?? []);
  console.log("[Map] createDeckLayers:", objectsArray.length, "объектов");

  // ========================================================================
  // СЛОИ ДЛЯ СУЩЕСТВУЮЩИХ ОБЪЕКТОВ
  // ========================================================================

  // Polygon fill layer
  const polygonFillObjects = objectsArray.filter(
    (obj) => obj.type === "Polygon" && obj.style.filled !== false
  );
  
  if (polygonFillObjects.length > 0) {
    layers.push(
      new PolygonLayer({
        id: "polygon-fill",
        data: polygonFillObjects,
        getPolygon: (obj: DeckGLObject) => obj.coordinates,
        getFillColor: (obj: DeckGLObject) => obj.style.color,
        getLineColor: [0, 0, 0, 0], // No outline from fill layer
        getElevation: 0,
        pickable: true,
        autoHighlight: true,
        onClick: (info: any) => {
          if (info.object) {
            selectObject((info.object as DeckGLObject).id);
          }
        },
      })
    );
    console.log("[Map] Polygon fill слой добавлен");
  }

  // Polygon/Polyline stroke layer
  const lineObjects = objectsArray.filter(
    (obj) => obj.type === "Polygon" || obj.type === "Polyline"
  );
  
  if (lineObjects.length > 0) {
    layers.push(
      new PathLayer({
        id: "polygon-stroke",
        data: lineObjects,
        getPath: (obj: DeckGLObject) => obj.coordinates,
        getColor: (obj: DeckGLObject) => obj.style.color,
        getWidth: (obj: DeckGLObject) => obj.style.strokeWidth ?? 2,
        getDashArray: (obj: DeckGLObject) => {
          const dash = obj.style.strokeDasharray;
          return dash && dash[0] > 0 ? dash : [0, 0];
        },
        pickable: true,
        autoHighlight: true,
        onClick: (info: any) => {
          if (info.object) {
            selectObject((info.object as DeckGLObject).id);
          }
        },
      })
    );
    console.log("[Map] Line слой добавлен");
  }

  // CircleMarker layer
  const pointObjects = objectsArray.filter(
    (obj) => obj.type === "CircleMarker"
  );
  
  if (pointObjects.length > 0) {
    layers.push(
      new ScatterplotLayer({
        id: "circle-marker",
        data: pointObjects,
        getPosition: (obj: DeckGLObject) => obj.coordinates[0] ?? [0, 0],
        getColor: (obj: DeckGLObject) => obj.style.color,
        getRadius: (obj: DeckGLObject) => obj.style.radius ?? 10,
        radiusMinPixels: 5,
        radiusMaxPixels: 20,
        pickable: true,
        autoHighlight: true,
        onClick: (info: any) => {
          if (info.object) {
            selectObject((info.object as DeckGLObject).id);
          }
        },
      })
    );
    console.log("[Map] CircleMarker слой добавлен");
  }

  // ========================================================================
  // СЛОЙ ДЛЯ DRAFT ОБЪЕКТА (в процессе создания)
  // ========================================================================
  
  if (DraftObject.value && DraftObject.value.coordinates.length > 0) {
    const draft = DraftObject.value;
    const draftColor = [255, 255, 0, 255] as [number, number, number, number];
    
    console.log("[Map] Draft объект:", draft.type, draft.coordinates.length, "точек");

    // CircleMarker - даже с 1 точкой
    if (draft.type === "CircleMarker" && draft.coordinates.length > 0) {
      layers.push(
        new ScatterplotLayer({
          id: "draft-circle",
          data: [draft],
          getPosition: (d: typeof draft) => d.coordinates[0] ?? [0, 0],
          getColor: draftColor,
          getRadius: 15,
          radiusMinPixels: 10,
          pickable: false,
        })
      );
      console.log("[Map] Draft CircleMarker слой добавлен");
    }
    // Polygon/Polyline - минимум 2 точки
    else if (draft.coordinates.length >= 2) {
      // Line layer для контура
      layers.push(
        new PathLayer({
          id: "draft-line",
          data: [draft],
          getPath: (d: typeof draft) => d.coordinates,
          getColor: draftColor,
          getWidth: 3,
          pickable: false,
        })
      );
      console.log("[Map] Draft Line слой добавлен");

      // Polygon fill - если >= 3 точек
      if (draft.type === "Polygon" && draft.coordinates.length >= 3) {
        layers.push(
          new PolygonLayer({
            id: "draft-polygon-fill",
            data: [draft],
            getPolygon: (d: typeof draft) => d.coordinates,
            getFillColor: [255, 255, 0, 100] as [number, number, number, number],
            getLineColor: [0, 0, 0, 0],
            pickable: false,
          })
        );
        console.log("[Map] Draft Polygon fill слой добавлен");
      }
    }
  }

  console.log("[Map] Всего слоёв Deck.gl:", layers.length);
  return layers;
};

// Инициализация карты
onMounted(() => {
  console.log("[Map] onMounted - начинаем инициализацию");
  
  try {
    // Создаём MapLibre map
    const map = new maplibregl.Map({
      container: "map",
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: [
              "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
              "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
              "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
            ],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap contributors',
          },
        },
        layers: [
          {
            id: "osm-tiles",
            type: "raster",
            source: "osm",
          },
        ],
      },
      center: [
        DeckGLMapConfig.initialViewState.longitude,
        DeckGLMapConfig.initialViewState.latitude,
      ],
      zoom: DeckGLMapConfig.initialViewState.zoom,
      pitch: DeckGLMapConfig.initialViewState.pitch,
      bearing: DeckGLMapConfig.initialViewState.bearing,
    });

    // Сохраняем instance
    mapInstance.value = map;
    console.log("[Map] MapLibre создана");

    // Создаём Deck.gl overlay
    deckOverlay = new MapboxOverlay({
      layers: createDeckLayers(),
      interleaved: true, // Важно для правильной отрисовки с MapLibre
    });

    // Добавляем Deck.gl как control
    map.addControl(deckOverlay);
    console.log("[Map] Deck.gl overlay добавлен");

    // Добавляем обработчик клика
    map.on("click", onMapClick);
    console.log("[Map] MapLibre click обработчик добавлен");

    // Применяем стили для курсоров
    map.on("load", () => {
      const canvas = map.getCanvas();
      if (canvas) {
        canvas.style.cursor = plusCursor.value;
      }
    });

    // Watch для реактивности - перерисовка при изменении объектов
    watch(
      () => Objects.value,
      () => {
        console.log("[Map] Objects изменился, перерисовка Deck.gl");
        if (deckOverlay) {
          deckOverlay.setProps({ layers: createDeckLayers() });
        }
      },
      { deep: true },
    );

    // Watch для draft объекта
    watch(
      () => DraftObject.value,
      () => {
        console.log(
          "[Map] Draft объект изменился:",
          DraftObject.value?.coordinates.length ?? 0,
          "точек",
        );
        if (deckOverlay) {
          deckOverlay.setProps({ layers: createDeckLayers() });
        }
      },
      { deep: true },
    );
  } catch (error) {
    console.error("[Map] Ошибка инициализации:", error);
  }
});

// Очистка при размонтировании
onUnmounted(() => {
  console.log("[Map] onUnmounted - очистка");
  if (deckOverlay) {
    deckOverlay.finalize();
    deckOverlay = null;
  }
  if (mapInstance.value) {
    mapInstance.value.remove();
    mapInstance.value = null;
  }
});
</script>

<template>
  <MapOptions
    :cancel-changes="cancelObject"
    :submit-changes="finalizeObject"
    :prev-action="undo"
    :next-action="redo"
    :can-undo="canUndo"
    :can-redo="canRedo"
  />
  <TilesSwitcher />
  <div class="flex-1 h-screen overflow-scroll">
    <div
      id="map"
      class="relative"
      :style="{
        cursor: isDragging ? grabCursor : plusCursor,
      }"
    ></div>
  </div>
</template>

<style scoped>
:deep(#map) {
  height: 100vh;
  width: 100vw;
  outline: none;
  user-select: none;
  position: relative;
}

/* MapLibre canvas */
:deep(.maplibregl-canvas) {
  cursor: inherit !important;
}

:deep(.maplibregl-canvas:active) {
  cursor: v-bind(grabCursor) !important;
}

/* Deck.gl canvas должен быть поверх MapLibre */
:deep(.deckgl-overlay) {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  z-index: 10 !important;
  pointer-events: none !important;
}
</style>
