<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import "leaflet/dist/leaflet.css";
import { storeToRefs } from "pinia";
import { LeafletMapConfig } from "@/config";
import { DeckGLMapConfig } from "@/config/DeckGLMapConfig";
import { useMapStore, useTilesStore } from "@/store";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { useDeckGL } from "@/composables/useDeckGL";
import MapOptions from "./MapOptions.vue";
import PlusCursor from "@/assets/plus-cursor.svg";
import GrabCursor from "@/assets/grab-cursor.svg";
import * as L from "leaflet";
import type { LngLatTuple, DeckGLObject } from "@/types";

// Импорт Deck.gl
import { DeckOverlay } from "@deck.gl-community/leaflet";
import { MapView } from "@deck.gl/core";
import { PathLayer, ScatterplotLayer } from "@deck.gl/layers";

const mapObjectStore = useMapObjectStore();
const mapStore = useMapStore();
const tilesStore = useTilesStore();

const { Objects, DraftObject } = storeToRefs(mapObjectStore);
const { mapInstance } = storeToRefs(mapStore);

// Курсоры
const plusCursor = computed(() => `url("${PlusCursor}") 16 16, auto`);
const grabCursor = computed(() => `url("${GrabCursor}") 16 16, auto`);

// Состояние для курсора
const isDragging = ref(false);

// Deck.gl composable
const {
  handleMapClick,
  finalizeObject,
  cancelObject,
  undo,
  redo,
  canUndo,
  canRedo,
} = useDeckGL();

// Ссылка на Deck.gl overlay
let deckOverlay: DeckOverlay | null = null;

// Слои Deck.gl
const deckLayers = computed(() => {
  const result: (PathLayer | ScatterplotLayer)[] = [];

  // Слои для существующих объектов
  Objects.value?.forEach((obj) => {
    if (obj.type === "Polygon") {
      // Контур полигона
      result.push(
        new PathLayer({
          id: `polygon-stroke-${obj.id}`,
          data: [obj],
          getPath: (d: DeckGLObject) => d.coordinates,
          getColor: obj.style.color,
          getWidth: obj.style.strokeWidth,
          getDashArray: obj.style.strokeDasharray ?? [0, 0],
          pickable: true,
          autoHighlight: true,
          onClick: () => selectObject(obj.id),
        }),
      );

      // Заливка полигона (если включена)
      if (obj.style.filled) {
        result.push(
          new PathLayer({
            id: `polygon-fill-${obj.id}`,
            data: [obj],
            getPath: (d: DeckGLObject) => d.coordinates,
            getColor: [
              ...obj.style.color.slice(0, 3),
              Math.round(obj.style.fillOpacity * 2.55),
            ] as [number, number, number, number],
            getWidth: 0,
            filled: true,
            pickable: false,
          }),
        );
      }
    } else if (obj.type === "Polyline") {
      result.push(
        new PathLayer({
          id: `polyline-${obj.id}`,
          data: [obj],
          getPath: (d: DeckGLObject) => d.coordinates,
          getColor: obj.style.color,
          getWidth: obj.style.strokeWidth,
          getDashArray: obj.style.strokeDasharray ?? [0, 0],
          pickable: true,
          autoHighlight: true,
          onClick: () => selectObject(obj.id),
        }),
      );
    } else if (obj.type === "CircleMarker") {
      result.push(
        new ScatterplotLayer({
          id: `circle-${obj.id}`,
          data: [obj],
          getPosition: (d: DeckGLObject): [number, number] => d.coordinates[0]!,
          getColor: obj.style.color,
          getRadius: 10,
          radiusMinPixels: 8,
          radiusMaxPixels: 20,
          pickable: true,
          autoHighlight: true,
          onClick: () => selectObject(obj.id),
        }),
      );
    }
  });

  // Слой для draft объекта (в процессе создания)
  if (DraftObject.value && DraftObject.value.coordinates.length > 0) {
    const draftLayer = createDraftLayer(DraftObject.value);
    if (draftLayer) {
      result.push(draftLayer);
    }
  }

  return result;
});

// Выделение объекта при клике
const selectObject = (id: string) => {
  mapObjectStore.ClickedObjId = id;
};

// Создание слоя для draft объекта
const createDraftLayer = (
  draft: typeof DraftObject.value,
): PathLayer | ScatterplotLayer | null => {
  if (!draft) return null;

  // Используем цвет из конфига для соответствия финальному объекту
  const color = DeckGLMapConfig.defaultStyles[draft.type]?.color ?? [
    255, 255, 0, 255,
  ];

  if (draft.type === "CircleMarker" && draft.coordinates.length > 0) {
    return new ScatterplotLayer({
      id: "draft-circle",
      data: [draft],
      getPosition: (d: typeof draft): [number, number] => d.coordinates[0]!,
      getColor: color,
      getRadius: 10,
      radiusMinPixels: 8,
      pickable: false,
    });
  } else if (draft.coordinates.length > 1) {
    return new PathLayer({
      id: "draft-path",
      data: [draft],
      getPath: (d: typeof draft): [number, number][] => d.coordinates,
      getColor: color,
      getWidth: 3,
      pickable: false,
    });
  }

  return null;
};

// Обработка клика по карте
const onMapClick = (e: L.LeafletMouseEvent) => {
  const latlng: LngLatTuple = [e.latlng.lng, e.latlng.lat];
  handleMapClick(latlng);
};

// Обработка перетаскивания
const onMapDragStart = () => {
  isDragging.value = true;
};

const onMapDragEnd = () => {
  isDragging.value = false;
};

// Инициализация карты
onMounted(() => {
  mapStore.initMap("map");

  if (mapInstance.value) {
    // Добавляем контроль атрибуции
    L.control
      .attribution({
        position: "topleft",
        prefix: "leaflet",
      })
      .addTo(mapInstance.value);

    // Добавляем тайловый слой
    L.tileLayer(tilesStore.$state.OSM.TilesURL, {
      attribution: LeafletMapConfig.OSMAttr,
    }).addTo(mapInstance.value);

    // Добавляем Deck.gl overlay
    deckOverlay = new DeckOverlay({
      views: [new MapView({ repeat: true })],
      layers: deckLayers.value,
    });
    mapInstance.value.addLayer(deckOverlay);

    // Следим за изменениями слоёв
    watch(deckLayers, (newLayers) => {
      if (deckOverlay) {
        deckOverlay.setProps({ layers: newLayers });
      }
    });

    // Обработчики событий
    mapInstance.value.on("click", onMapClick);
    mapInstance.value.on("dragstart", onMapDragStart);
    mapInstance.value.on("dragend", onMapDragEnd);
  } else {
    console.error("Map component unregistered ref");
  }
});

// Очистка при размонтировании
onUnmounted(() => {
  if (mapInstance.value) {
    mapInstance.value.off("click", onMapClick);
    mapInstance.value.off("dragstart", onMapDragStart);
    mapInstance.value.off("dragend", onMapDragEnd);
  }

  // Удаляем Deck.gl overlay
  if (deckOverlay) {
    deckOverlay.remove();
    deckOverlay = null;
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
  <div class="flex-1 h-screen overflow-scroll">
    <div
      id="map"
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
}

:deep(.leaflet-container) {
  cursor: v-bind(plusCursor) !important;
}

:deep(.leaflet-drag-target) {
  cursor: v-bind(grabCursor) !important;
}
</style>
