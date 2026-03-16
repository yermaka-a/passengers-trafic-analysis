<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, shallowRef } from "vue";
import "maplibre-gl/dist/maplibre-gl.css";
import { storeToRefs } from "pinia";
import { useMapStore } from "@/store";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { useL7 } from "@/composables/useL7";
import { TilesSwitcher } from "@/components/TilesSwitcher";
import MapOptions from "./MapOptions.vue";
import PlusCursor from "@/assets/plus-cursor.svg";
import GrabCursor from "@/assets/grab-cursor.svg";
import type { LngLatTuple } from "@/types";

// AntV L7 imports - используем правильный импорт для L7 2.x
import { Scene, PolygonLayer, LineLayer, PointLayer } from "@antv/l7";

const mapObjectStore = useMapObjectStore();
const mapStore = useMapStore();

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

// Обработка клика по карте
const onMapClick = (e: any) => {
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
  const layers = l7Scene.value.getLayers();
  layers.forEach((layer: any) => {
    l7Scene.value?.removeLayer(layer);
  });

  const objectsArray = Array.from(Objects.value?.values() ?? []);
  console.log("[Map] Создаём слои, объектов:", objectsArray.length);

  // Polygon слой (заливка)
  const polygonData = objectsArray
    .filter((obj) => obj.type === "Polygon" && obj.style.filled)
    .map((obj) => ({
      id: obj.id,
      coordinates: obj.coordinates,
      fillColor: obj.style.fillColor ?? [0, 128, 255, 180],
      fillOpacity: obj.style.fillOpacity ?? 0.5,
    }));

  if (polygonData.length > 0) {
    const polygonLayer = new PolygonLayer({
      autoFit: false,
    })
      .source({
        type: "json",
        data: {
          type: "FeatureCollection",
          features: polygonData.map((obj) => ({
            type: "Feature",
            properties: {
              id: obj.id,
              fillColor: obj.fillColor,
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
      .color("fillColor")
      .style({
        opacity: 1,
      });

    l7Scene.value.addLayer(polygonLayer);
    console.log("[Map] Polygon fill слой добавлен");
  }

  // Line слой (для контуров полигонов и полилиний)
  const lineData = objectsArray
    .filter((obj) => obj.type === "Polygon" || obj.type === "Polyline")
    .map((obj) => ({
      id: obj.id,
      coordinates: obj.coordinates,
      strokeColor: obj.style.strokeColor ?? [0, 128, 255, 255],
      strokeWidth: obj.style.strokeWidth ?? 3,
    }));

  if (lineData.length > 0) {
    const lineLayer = new LineLayer({
      autoFit: false,
    })
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
            },
            geometry: {
              type: "LineString",
              coordinates: obj.coordinates,
            },
          })),
        },
      })
      .shape("line")
      .size("strokeWidth")
      .color("strokeColor")
      .style({
        lineType: "dash",
      });

    l7Scene.value.addLayer(lineLayer);
    console.log("[Map] Line слой добавлен");
  }

  // Point слой (для CircleMarker)
  const pointData = objectsArray
    .filter((obj) => obj.type === "CircleMarker")
    .map((obj) => ({
      id: obj.id,
      coordinates: obj.coordinates[0], // Первая точка
      fillColor: obj.style.fillColor ?? [0, 255, 0, 255],
      radius: 10,
    }));

  if (pointData.length > 0) {
    const pointLayer = new PointLayer({
      autoFit: false,
    })
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
      .size("radius")
      .color("fillColor")
      .style({
        opacity: 1,
      });

    l7Scene.value.addLayer(pointLayer);
    console.log("[Map] Point слой добавлен");
  }
};

// Инициализация карты
onMounted(async () => {
  mapStore.initMap("map");

  if (mapInstance.value) {
    // Ждём загрузки карты
    mapInstance.value.on("load", async () => {
      console.log("[Map] MapLibre загружена");

      // Создаём L7 Scene с правильной конфигурацией для L7 2.x
      // Используем async/await для инициализации
      try {
        l7Scene.value = new Scene({
          id: "map",
          map: mapInstance.value as any,
        });

        // Ждём инициализации сцены
        l7Scene.value.on("loaded", () => {
          console.log("[Map] L7 Scene загружена");
          createLayers();
        });
      } catch (error) {
        console.error("[Map] Ошибка инициализации L7 Scene:", error);
      }
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
