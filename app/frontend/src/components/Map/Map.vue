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
import type { LngLatTuple } from "@/types";

// Импорт Deck.gl
import { DeckOverlay } from "@deck.gl-community/leaflet";
import { MapView } from "@deck.gl/core";
import { PathLayer, ScatterplotLayer, PolygonLayer } from "@deck.gl/layers";
import { PathStyleExtension } from "@deck.gl/extensions";

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
let deckOverlay: (DeckOverlay & { _deck?: any }) | null = null;

// Слои Deck.gl
const deckLayers = computed(() => {
  const result: (PathLayer | ScatterplotLayer | PolygonLayer)[] = [];

  // Force reactivity - явно читаем Objects.value
  const objectsCount = Objects.value?.size ?? 0;
  console.log("[Map] deckLayers вычисляется, объектов:", objectsCount);

  // Слои для существующих объектов
  Objects.value?.forEach((obj) => {
    // Явно читаем все свойства для реактивности
    const color = obj.style.color;
    const strokeWidth = obj.style.strokeWidth;
    const strokeDasharray = obj.style.strokeDasharray;
    const filled = obj.style.filled;
    const fillOpacity = obj.style.fillOpacity;

    // Создаём чистый объект без Proxy для Deck.gl
    const layerData = {
      id: obj.id,
      type: obj.type,
      coordinates: obj.coordinates.map(
        (coord: LngLatTuple) => [coord[0]!, coord[1]!] as [number, number],
      ),
      style: {
        color,
        strokeWidth,
        strokeDasharray,
        filled,
        fillOpacity,
      },
    };

    if (obj.type === "Polygon") {
      // Заливка полигона (если включена) - используем PolygonLayer
      if (obj.style.filled) {
        result.push(
          new PolygonLayer({
            id: `polygon-fill-${obj.id}`,
            data: [layerData],
            getPolygon: (d: typeof layerData) => d.coordinates,
            getFillColor: (d: typeof layerData) =>
              [
                ...d.style.color.slice(0, 3),
                Math.round(d.style.fillOpacity * 255),
              ] as [number, number, number, number],
            getLineColor: [0, 0, 0, 0],
            pickable: false,
            stroked: false,
            filled: true,
          }),
        );
      }

      // Контур полигона
      result.push(
        new PathLayer({
          id: `polygon-stroke-${obj.id}`,
          data: [layerData],
          getPath: (d: typeof layerData) => d.coordinates,
          getLineColor: () => color,
          getWidth: () => strokeWidth,
          getDashArray: () =>
            strokeDasharray && strokeDasharray[0] > 0
              ? strokeDasharray
              : [0, 0],
          extensions: [new PathStyleExtension({ dash: true })],
          pickable: true,
          autoHighlight: true,
          onClick: () => selectObject(obj.id),
          updateTriggers: {
            getLineColor: [color],
            getWidth: [strokeWidth],
            getDashArray: [strokeDasharray],
          },
        }),
      );
    } else if (obj.type === "Polyline") {
      result.push(
        new PathLayer({
          id: `polyline-${obj.id}`,
          data: [layerData],
          getPath: (d: typeof layerData) => d.coordinates,
          getLineColor: () => color,
          getWidth: () => strokeWidth,
          getDashArray: () =>
            strokeDasharray && strokeDasharray[0] > 0
              ? strokeDasharray
              : [0, 0],
          extensions: [new PathStyleExtension({ dash: true })],
          pickable: true,
          autoHighlight: true,
          onClick: () => selectObject(obj.id),
          updateTriggers: {
            getLineColor: [color],
            getWidth: [strokeWidth],
            getDashArray: [strokeDasharray],
          },
        }),
      );
    } else if (obj.type === "CircleMarker") {
      result.push(
        new ScatterplotLayer({
          id: `circle-${obj.id}`,
          data: [layerData],
          getPosition: (d: typeof layerData): [number, number] =>
            d.coordinates[0]!,
          getFillColor: () => color,
          getLineColor: [0, 0, 0, 0],
          getRadius: 10,
          radiusMinPixels: 8,
          radiusMaxPixels: 20,
          pickable: true,
          autoHighlight: true,
          onClick: () => selectObject(obj.id),
          updateTriggers: {
            getFillColor: [color],
          },
        }),
      );
    }
  });

  // Слой для draft объекта (в процессе создания)
  if (DraftObject.value && DraftObject.value.coordinates.length > 0) {
    console.log(
      "[Map] Draft объект:",
      DraftObject.value.type,
      DraftObject.value.coordinates.length,
      "точек",
    );

    // Для CircleMarker показываем даже с 1 точкой
    if (DraftObject.value.type === "CircleMarker") {
      const draftLayer = createDraftLayer(DraftObject.value);
      if (draftLayer) {
        console.log("[Map] Draft слой создан");
        result.push(draftLayer);
      }
    } else if (DraftObject.value.coordinates.length >= 2) {
      // Для Polygon/Polyline нужно минимум 2 точки
      const draftLayer = createDraftLayer(DraftObject.value);
      if (draftLayer) {
        console.log("[Map] Draft слой создан");
        result.push(draftLayer);
      }
    }
  }

  console.log("[Map] Всего слоёв:", result.length);
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

  // Конвертируем координаты из Proxy
  const coordinates = draft.coordinates.map(
    (coord: LngLatTuple) => [coord[0], coord[1]] as [number, number],
  );

  if (draft.type === "CircleMarker" && coordinates.length > 0) {
    return new ScatterplotLayer({
      id: "draft-circle",
      data: [{ ...draft, coordinates }],
      getPosition: (
        d: typeof draft & { coordinates: [number, number][] },
      ): [number, number] => d.coordinates[0]!,
      getFillColor: color,
      getLineColor: [0, 0, 0, 0],
      getRadius: 10,
      radiusMinPixels: 8,
      pickable: false,
    });
  } else if (coordinates.length > 1) {
    return new PathLayer({
      id: "draft-path",
      data: [{ ...draft, coordinates }],
      getPath: (
        d: typeof draft & { coordinates: [number, number][] },
      ): [number, number][] => d.coordinates,
      getLineColor: color,
      getWidth: 3,
      pickable: false,
    });
  }

  return null;
};

// Обработка клика по карте
const onMapClick = (e: L.LeafletMouseEvent) => {
  const latlng: LngLatTuple = [e.latlng.lng, e.latlng.lat];
  console.log("[Map] Клик:", latlng, "Leaflet:", e.latlng);
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
    console.log("[Map] Deck.gl overlay добавлен");
    console.log("[Map] deckOverlay:", deckOverlay);

    // Следим за изменениями в Objects - принудительная реактивность
    watch(
      () => Objects.value,
      (newObjects) => {
        console.log("[Map] Objects изменился:", newObjects?.size ?? 0);
        // Принудительно обновляем layers
        if (deckOverlay && deckOverlay._deck) {
          console.log(
            "[Map] Принудительное обновление layers:",
            deckLayers.value.length,
          );
          // Полностью заменяем слои
          deckOverlay._deck.setProps({
            layers: deckLayers.value,
            // Принудительная перерисовка
            _animate: true,
          });
          // Вызываем redraw для гарантии
          setTimeout(() => {
            if (deckOverlay?._deck) {
              deckOverlay._deck.redraw();
            }
          }, 50);
        }
      },
      { deep: true },
    );

    // Следим за DraftObject - перерисовка при создании
    watch(
      () => DraftObject.value,
      (newDraft) => {
        console.log(
          "[Map] Draft объект изменился:",
          newDraft?.coordinates.length ?? 0,
          "точек",
        );
        // Принудительно обновляем layers
        if (deckOverlay && deckOverlay._deck) {
          console.log(
            "[Map] Принудительное обновление layers для draft:",
            deckLayers.value.length,
          );
          deckOverlay._deck.setProps({
            layers: deckLayers.value,
            _animate: true,
          });
          setTimeout(() => {
            if (deckOverlay?._deck) {
              deckOverlay._deck.redraw();
            }
          }, 50);
        }
      },
      { deep: true },
    );

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
  position: relative;
  z-index: 1;
}

:deep(.leaflet-container) {
  cursor: v-bind(plusCursor) !important;
}

:deep(.leaflet-drag-target) {
  cursor: v-bind(grabCursor) !important;
}

/* Deck.gl canvas должен быть поверх Leaflet */
:deep(.deckgl-overlay) {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  pointer-events: none;
}
</style>
