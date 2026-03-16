<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, shallowRef } from "vue";
import "maplibre-gl/dist/maplibre-gl.css";
import { storeToRefs } from "pinia";
import { useMapStore, useTilesStore } from "@/store";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { useL7 } from "@/composables/useL7";
import { TilesSwitcher } from "@/components/TilesSwitcher";
import MapOptions from "./MapOptions.vue";
import PlusCursor from "@/assets/plus-cursor.svg";
import GrabCursor from "@/assets/grab-cursor.svg";
import type { Map, MapMouseEvent } from "maplibre-gl";
import type { LngLatTuple } from "@/types";
import { L7MapConfig } from "@/config/L7MapConfig";

// AntV L7 imports
import { Scene, PolygonLayer, LineLayer, PointLayer } from "@antv/l7";

const mapObjectStore = useMapObjectStore();
const mapStore = useMapStore();
const tilesStore = useTilesStore();

const { Objects, DraftObject } = storeToRefs(mapObjectStore);
const { mapInstance } = storeToRefs(mapStore);

// L7 Scene
const l7Scene = shallowRef<Scene | null>(null);

// Курсоры
const plusCursor = computed(() => `url("${PlusCursor}") 16 16, auto`);
const grabCursor = computed(() => `url("${GrabCursor}") 16 16, auto`);

// Состояние для курсора
const isDragging = ref(false);

// L7 composable
const {
  handleMapClick,
  finalizeObject,
  cancelObject,
  undo,
  redo,
  canUndo,
  canRedo,
} = useL7();

// Выделение объекта при клике
const selectObject = (id: string) => {
  mapObjectStore.ClickedObjId = id;
};

// Обработка клика по карте
const onMapClick = (e: MapMouseEvent) => {
  const lngLat: LngLatTuple = [e.lngLat.lng, e.lngLat.lat];
  console.log("[Map] Клик:", lngLat);
  handleMapClick(lngLat);
};

// Обработка перетаскивания
const onMapDragStart = () => {
  isDragging.value = true;
};

const onMapDragEnd = () => {
  isDragging.value = false;
};

// Создание слоёв L7
const createLayers = () => {
  if (!l7Scene.value) return;

  // Очищаем старые слои
  l7Scene.value.layers.forEach((layer) => {
    l7Scene.value?.removeLayer(layer);
  });

  const objectsArray = Array.from(Objects.value?.values() ?? []);
  console.log("[Map] Создаём слои, объектов:", objectsArray.length);

  // Polygon слой
  const polygonData = objectsArray
    .filter((obj) => obj.type === "Polygon")
    .map((obj) => ({
      id: obj.id,
      coordinates: obj.coordinates,
      fillColor: obj.style.fillColor ?? [0, 128, 255, 180],
      strokeColor: obj.style.strokeColor ?? [0, 128, 255, 255],
      strokeWidth: obj.style.strokeWidth ?? 3,
      filled: obj.style.filled ?? true,
      fillOpacity: obj.style.fillOpacity ?? 0.5,
    }));

  if (polygonData.length > 0) {
    const polygonLayer = new PolygonLayer({})
      .source({
        type: "json",
        data: {
          type: "FeatureCollection",
          features: polygonData.map((obj) => ({
            type: "Feature",
            properties: {
              id: obj.id,
              fillColor: obj.fillColor,
              strokeColor: obj.strokeColor,
              strokeWidth: obj.strokeWidth,
              filled: obj.filled,
              fillOpacity: obj.fillOpacity,
            },
            geometry: {
              type: "Polygon",
              coordinates: [obj.coordinates],
            },
          })),
        },
      })
      .shape("fill")
      .color("fillColor", (c: number[]) => c as [number, number, number, number])
      .active("id", (id: string) => {
        selectObject(id);
      })
      .style({
        opacity: 1,
      });

    l7Scene.value.addLayer(polygonLayer);
  }

  // Line слой (для контуров полигонов и полилиний)
  const lineData = objectsArray
    .filter((obj) => obj.type === "Polygon" || obj.type === "Polyline")
    .map((obj) => ({
      id: obj.id,
      coordinates: obj.coordinates,
      strokeColor: obj.style.strokeColor ?? [255, 0, 0, 255],
      strokeWidth: obj.style.strokeWidth ?? 3,
      strokeDasharray: obj.style.strokeDasharray ?? [0, 0],
    }));

  if (lineData.length > 0) {
    const lineLayer = new LineLayer({})
      .source({
        type: "json",
        data: {
          type: "FeatureCollection",
          features: lineData.map((obj) => ({
            type: "Feature",
            properties: {
              id: obj.id,
              strokeColor: obj.strokeColor,
              strokeWidth: obj.strokeWidth,
              strokeDasharray: obj.strokeDasharray,
            },
            geometry: {
              type: "LineString",
              coordinates: obj.coordinates,
            },
          })),
        },
      })
      .shape("line")
      .size("strokeWidth", (w: number) => w)
      .color("strokeColor", (c: number[]) => c as [number, number, number, number])
      .active("id", (id: string) => {
        selectObject(id);
      })
      .style({
        lineType: "dash",
      });

    l7Scene.value.addLayer(lineLayer);
  }

  // Point слой (для CircleMarker)
  const pointData = objectsArray
    .filter((obj) => obj.type === "CircleMarker")
    .map((obj) => ({
      id: obj.id,
      coordinates: obj.coordinates[0], // Первая точка
      fillColor: obj.style.fillColor ?? [0, 255, 0, 255],
      radius: obj.style.radius ?? 10,
    }));

  if (pointData.length > 0) {
    const pointLayer = new PointLayer({})
      .source({
        type: "json",
        data: {
          type: "FeatureCollection",
          features: pointData.map((obj) => ({
            type: "Feature",
            properties: {
              id: obj.id,
              fillColor: obj.fillColor,
              radius: obj.radius,
            },
            geometry: {
              type: "Point",
              coordinates: obj.coordinates,
            },
          })),
        },
      })
      .shape("circle")
      .size("radius", (r: number) => r)
      .color("fillColor", (c: number[]) => c as [number, number, number, number])
      .active("id", (id: string) => {
        selectObject(id);
      })
      .style({
        opacity: 1,
      });

    l7Scene.value.addLayer(pointLayer);
  }
};

// Инициализация карты
onMounted(async () => {
  mapStore.initMap("map");

  if (mapInstance.value) {
    // Ждём загрузки карты
    mapInstance.value.on("load", () => {
      console.log("[Map] MapLibre загружена");

      // Создаём L7 Scene
      l7Scene.value = new Scene({
        id: "map",
        map: mapInstance.value,
        ...L7MapConfig.scene,
      });

      // Ждём инициализации сцены
      l7Scene.value.on("loaded", () => {
        console.log("[Map] L7 Scene загружена");
        createLayers();
      });
    });

    // Обработчики событий
    mapInstance.value.on("click", onMapClick);
    mapInstance.value.on("dragstart", onMapDragStart);
    mapInstance.value.on("dragend", onMapDragEnd);
  } else {
    console.error("[Map] Map instance не создана");
  }
});

// Watch для реактивности - перерисовка при изменении объектов
watch(
  () => Objects.value,
  () => {
    console.log("[Map] Objects изменился, перерисовка:", Objects.value.size);
    if (l7Scene.value) {
      createLayers();
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
    if (l7Scene.value) {
      createLayers();
    }
  },
  { deep: true },
);

// Очистка при размонтировании
onUnmounted(() => {
  if (mapInstance.value) {
    mapInstance.value.off("click", onMapClick);
    mapInstance.value.off("dragstart", onMapDragStart);
    mapInstance.value.off("dragend", onMapDragEnd);
  }

  if (l7Scene.value) {
    l7Scene.value.destroy();
    l7Scene.value = null;
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

:deep(.maplibregl-canvas) {
  cursor: v-bind(plusCursor) !important;
}

:deep(.maplibregl-canvas.dragging) {
  cursor: v-bind(grabCursor) !important;
}
</style>
