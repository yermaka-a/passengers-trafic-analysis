<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl from "maplibre-gl";
import { storeToRefs } from "pinia";
import { useMapObjectStore, useMapStore } from "@/store";
import { useL7 } from "@/composables/useL7";
import { TilesSwitcher } from "@/components/TilesSwitcher";
import MapOptions from "./MapOptions.vue";
import PlusCursor from "@/assets/plus-cursor.svg";
import GrabCursor from "@/assets/grab-cursor.svg";
import type { LngLatTuple, DeckGLObject } from "@/types";

// Deck.gl imports
import { MapboxOverlay } from "@deck.gl/mapbox";
import { PolygonLayer, PathLayer, ScatterplotLayer } from "@deck.gl/layers";
import { PathStyleExtension } from "@deck.gl/extensions";
import { DeckGLMapConfig } from "@/config/DeckGLMapConfig";

const mapObjectStore = useMapObjectStore();
const mapStore = useMapStore();

const { Objects, DraftObject } = storeToRefs(mapObjectStore);

// MapLibre instance
const mapInstance = ref<maplibregl.Map | null>(null);

// Deck.gl overlay
let deckOverlay: MapboxOverlay | null = null;

// Draft object color (default red)
const draftColor = ref("#ff0000");

// Convert hex to RGBA for Deck.gl
const hexToRGBA = (hex: string, alpha: number = 255): [number, number, number, number] => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return [255, 0, 0, alpha];
  return [
    Number.parseInt(result[1]!, 16),
    Number.parseInt(result[2]!, 16),
    Number.parseInt(result[3]!, 16),
    alpha,
  ];
};

// Курсоры
const plusCursor = computed(() => `url("${PlusCursor}") 16 16, auto`);
const grabCursor = computed(() => `url("${GrabCursor}") 16 16, auto`);

// L7 composable (переименовать потом в useDeckGL)
const {
  handleMapClick,
  finalizeObject: finalizeObjectFromComposable,
  cancelObject,
  undo,
  redo,
  canUndo,
  canRedo,
} = useL7();

// Wrapper для передачи цвета
const finalizeObject = async () => {
  await finalizeObjectFromComposable(draftColor.value);
};

// Обновляем цвет draft объекта при изменении
watch(draftColor, (newColor) => {
  const draft = mapObjectStore.getDraftObject;
  if (draft) {
    const rgbaColor = hexToRGBA(newColor, 255);
    mapObjectStore.updateDraftStyle({ color: rgbaColor });
  }
});

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

  // Polygon fill layer (и Polyline если filled=true)
  const polygonFillObjects = objectsArray.filter(
    (obj) => (obj.type === "Polygon" || obj.type === "Polyline") && obj.style.filled !== false
  );
  
  if (polygonFillObjects.length > 0) {
    layers.push(
      new PolygonLayer({
        id: "polygon-fill",
        data: polygonFillObjects,
        getPolygon: (obj: DeckGLObject) => obj.coordinates,
        getFillColor: (obj: DeckGLObject) => {
          // Применяем прозрачность fillOpacity к цвету
          const color = obj.style.color;
          return [
            color[0]!,
            color[1]!,
            color[2]!,
            Math.round(color[3]! * (obj.style.fillOpacity ?? 0.5))
          ] as [number, number, number, number];
        },
        updateTriggers: {
          getFillColor: polygonFillObjects.map(o => ({ id: o.id, color: o.style.color, fillOpacity: o.style.fillOpacity })),
        },
        getLineColor: [0, 0, 0, 0], // No outline from fill layer
        getElevation: 0,
        pickable: false,  // Заливка не должна перехватывать клики
        stroked: false,
        filled: true,
      })
    );
    console.log("[Map] Polygon fill слой добавлен");
  }

  // Polygon/Polyline stroke layer
  const lineObjects = objectsArray.filter(
    (obj) => obj.type === "Polygon" || obj.type === "Polyline"
  );

  if (lineObjects.length > 0) {
    console.log("[Map] Line объекты:", lineObjects.map(o => ({ 
      id: o.id, 
      color: o.style.color, 
      strokeWidth: o.style.strokeWidth,
      strokeDasharray: o.style.strokeDasharray 
    })));
    
    // Создаём PathStyleExtension для поддержки пунктира
    const pathStyleExtension = new PathStyleExtension({
      dash: true,
      highPrecision: false,
    });
    
    // Логи для updateTriggers
    const dashTriggers = lineObjects.map(o => ({ id: o.id, strokeDasharray: o.style.strokeDasharray }));
    console.log("[Map] updateTriggers.getDashArray:", dashTriggers);
    
    layers.push(
      new PathLayer({
        id: "polygon-stroke",
        data: lineObjects,
        getPath: (obj: DeckGLObject) => obj.coordinates,
        getColor: (obj: DeckGLObject) => {
          console.log("[Map] getColor для", obj.id, ":", obj.style.color);
          return obj.style.color;
        },
        getWidth: (obj: DeckGLObject) => {
          console.log("[Map] getWidth для", obj.id, ":", obj.style.strokeWidth);
          return obj.style.strokeWidth ?? 2;
        },
        getDashArray: (obj: DeckGLObject) => {
          const dash = obj.style.strokeDasharray;
          console.log("[Map] getDashArray для", obj.id, ":", dash, "dash[0]:", dash?.[0]);
          // Возвращаем [0, 0] если пунктир выключен
          return dash && dash[0] && dash[0] > 0 ? dash : [0, 0];
        },
        updateTriggers: {
          getColor: lineObjects.map(o => ({ id: o.id, color: o.style.color })),
          getWidth: lineObjects.map(o => ({ id: o.id, strokeWidth: o.style.strokeWidth })),
          getDashArray: dashTriggers,
        },
        extensions: [pathStyleExtension],
        pickable: true,
        autoHighlight: true,
        onClick: (info: any) => {
          if (info.object) {
            selectObject((info.object as DeckGLObject).id);
          }
        },
      })
    );
    console.log("[Map] Line слой добавлен с PathStyleExtension");
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
        // Заливка маркера
        getColor: (obj: DeckGLObject) => {
          const color = obj.style.color;
          // Применяем fillOpacity к альфа-каналу
          return [
            color[0]!,
            color[1]!,
            color[2]!,
            Math.round(color[3]! * (obj.style.fillOpacity ?? 1.0))
          ];
        },
        getRadius: (obj: DeckGLObject) => obj.style.radius ?? 10,
        radiusMinPixels: 5,
        radiusMaxPixels: 20,
        // Обводка маркера
        getLineColor: (obj: DeckGLObject) => {
          // Если обводка выключена (strokeWidth=0), возвращаем прозрачный
          if ((obj.style.strokeWidth ?? 0) === 0) {
            return [0, 0, 0, 0];
          }
          return obj.style.color;
        },
        getLineWidth: (obj: DeckGLObject) => obj.style.strokeWidth ?? 0,
        getLineDashArray: (obj: DeckGLObject) => {
          const dash = obj.style.strokeDasharray;
          return dash && dash[0] && dash[0] > 0 ? dash : [0, 0];
        },
        updateTriggers: {
          getColor: pointObjects.map(o => ({ id: o.id, color: o.style.color, fillOpacity: o.style.fillOpacity })),
          getRadius: pointObjects.map(o => ({ id: o.id, radius: o.style.radius })),
          getLineColor: pointObjects.map(o => ({ id: o.id, color: o.style.color, strokeWidth: o.style.strokeWidth })),
          getLineWidth: pointObjects.map(o => ({ id: o.id, strokeWidth: o.style.strokeWidth })),
          getLineDashArray: pointObjects.map(o => ({ id: o.id, strokeDasharray: o.style.strokeDasharray })),
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
    console.log("[Map] CircleMarker слой добавлен");
  }

  // ========================================================================
  // СЛОЙ ДЛЯ DRAFT ОБЪЕКТА (в процессе создания)
  // ========================================================================

  if (DraftObject.value && DraftObject.value.coordinates.length > 0) {
    const draft = DraftObject.value;
    // Используем цвет из state
    const draftColorRGBA = hexToRGBA(draftColor.value, 255);
    const draftColorRGBATransparent = hexToRGBA(draftColor.value, 100);

    // CircleMarker - даже с 1 точкой
    if (draft.type === "CircleMarker" && draft.coordinates.length > 0) {
      layers.push(
        new ScatterplotLayer({
          id: "draft-circle",
          data: [draft],
          getPosition: (d: typeof draft) => d.coordinates[0] ?? [0, 0],
          getColor: draftColorRGBA,
          getRadius: 15,
          radiusMinPixels: 10,
          pickable: false,
        })
      );
    }
    // Polygon/Polyline - минимум 2 точки
    else if (draft.coordinates.length >= 2) {
      // Line layer для контура
      layers.push(
        new PathLayer({
          id: "draft-line",
          data: [draft],
          getPath: (d: typeof draft) => d.coordinates,
          getColor: draftColorRGBA,
          getWidth: 3,
          pickable: false,
        })
      );

      // Polygon fill - если >= 3 точек
      if (draft.type === "Polygon" && draft.coordinates.length >= 3) {
        layers.push(
          new PolygonLayer({
            id: "draft-polygon-fill",
            data: [draft],
            getPolygon: (d: typeof draft) => d.coordinates,
            getFillColor: draftColorRGBATransparent,
            getLineColor: [0, 0, 0, 0],
            pickable: false,
          })
        );
      }
    }
  }

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
    mapStore.mapInstance = map;  // Сохраняем в store для доступа из List.vue
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

    // Применяем стили для курсоров через CSS
    // Курсоры управляются через CSS классы maplibregl-map и maplibregl-canvas:active

    // Watch для реактивности - перерисовка при изменении объектов
    // Используем Array.from для реактивности Map
    watch(
      () => Array.from(Objects.value?.values() ?? []),
      (newObjects) => {
        console.log("[Map] Objects изменился:", newObjects.length);
        // Принудительно обновляем layers для Deck.gl
        if (deckOverlay && deckOverlay._deck) {
          deckOverlay._deck.setProps({
            layers: createDeckLayers(),
            _animate: true,
          });
          // Принудительная перерисовка для применения стилей
          setTimeout(() => {
            if (deckOverlay?._deck) {
              deckOverlay._deck.redraw();
            }
          }, 50);
        }
      },
      { deep: true },
    );

    // Watch для draft объекта
    watch(
      () => DraftObject.value,
      (newDraft) => {
        console.log(
          "[Map] Draft объект изменился:",
          newDraft?.coordinates.length ?? 0,
          "точек",
        );
        if (deckOverlay && deckOverlay._deck) {
          deckOverlay._deck.setProps({
            layers: createDeckLayers(),
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
    :draft-color="draftColor"
    @update:draft-color="draftColor = $event"
  />
  <TilesSwitcher />
  <div class="flex-1 h-screen overflow-scroll">
    <div
      id="map"
      class="relative"
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
  cursor: v-bind(plusCursor) !important;
}

:deep(.maplibregl-map) {
  cursor: v-bind(plusCursor) !important;
}

:deep(.maplibregl-canvas) {
  cursor: v-bind(plusCursor) !important;
}

:deep(.maplibregl-canvas:active),
:deep(.maplibregl-map.dragging) {
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
