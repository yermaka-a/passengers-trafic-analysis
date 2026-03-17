<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import "maplibre-gl/dist/maplibre-gl.css";
import { storeToRefs } from "pinia";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { useL7 } from "@/composables/useL7";
import { TilesSwitcher } from "@/components/TilesSwitcher";
import MapOptions from "./MapOptions.vue";
import PlusCursor from "@/assets/plus-cursor.svg";
import GrabCursor from "@/assets/grab-cursor.svg";
import type { LngLatTuple } from "@/types";

// AntV L7 imports
import { Scene, PolygonLayer, LineLayer, PointLayer } from "@antv/l7";
import { MapLibre } from "@antv/l7-maps";

const mapObjectStore = useMapObjectStore();

const { Objects, DraftObject } = storeToRefs(mapObjectStore);

// L7 Scene
const l7Scene = ref<Scene | null>(null);
const mapInstance = ref<any>(null);

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

// Выделение объекта при клике
const selectObject = (id: string) => {
  console.log("[Map] Select object:", id);
  mapObjectStore.ClickedObjId = id;
};

// Создание слоёв L7
const createLayers = () => {
  console.log("[Map] createLayers вызван");
  console.log("[Map] l7Scene.value:", l7Scene.value);
  console.log("[Map] Objects.value.size:", Objects.value?.size);

  if (!l7Scene.value) {
    console.error("[Map] l7Scene.value отсутствует");
    return;
  }

  // Очищаем старые слои
  const layers = l7Scene.value.getLayers();
  console.log("[Map] Слоёв до очистки:", layers.length);
  layers.forEach((layer: any) => {
    l7Scene.value?.removeLayer(layer);
  });

  const objectsArray = Array.from(Objects.value?.values() ?? []);
  console.log("[Map] Создаём слои, объектов:", objectsArray.length);
  console.log(
    "[Map] Объекты:",
    objectsArray.map((o) => ({ id: o.id, type: o.type, style: o.style })),
  );

  // Polygon слой (заливка)
  const polygonFillData = objectsArray
    .filter((obj) => obj.type === "Polygon" && obj.style.filled !== false)
    .map((obj) => ({
      id: obj.id,
      coordinates: obj.coordinates,
      fillColor: obj.style.fillColor ?? [0, 128, 255, 128],
      fillOpacity: obj.style.fillOpacity ?? 0.3,
    }));

  console.log("[Map] Polygon fill данные:", polygonFillData.length, "объектов");
  if (polygonFillData.length > 0) {
    console.log("[Map] Первый polygon:", polygonFillData[0]);
  }

  if (polygonFillData.length > 0) {
    const polygonFillLayer = new PolygonLayer({
      autoFit: false,
    })
      .source({
        type: "json",
        data: {
          type: "FeatureCollection",
          features: polygonFillData.map((obj) => ({
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
      .active(true)
      .style({
        opacity: 1,
      });

    // Добавляем обработчик клика на слой
    polygonFillLayer.on("click", (e: any) => {
      console.log("[Map] Polygon layer click:", e);
      if (e.feature?.properties?.id) {
        selectObject(e.feature.properties.id);
      }
    });

    l7Scene.value.addLayer(polygonFillLayer);
    console.log("[Map] Polygon fill слой добавлен");
  }

  // Polygon/Polyline слой (контур)
  const lineData = objectsArray
    .filter((obj) => obj.type === "Polygon" || obj.type === "Polyline")
    .map((obj) => ({
      id: obj.id,
      coordinates: obj.coordinates,
      strokeColor: obj.style.strokeColor ?? [0, 128, 255, 255],
      strokeWidth: obj.style.strokeWidth ?? 3,
    }));

  console.log("[Map] Line данные:", lineData.length, "объектов");
  if (lineData.length > 0) {
    console.log("[Map] Первая линия:", lineData[0]);
  }

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
      .active(true)
      .style({
        lineType: "solid",
      });

    // Добавляем обработчик клика на слой
    lineLayer.on("click", (e: any) => {
      console.log("[Map] Line layer click:", e);
      if (e.feature?.properties?.id) {
        selectObject(e.feature.properties.id);
      }
    });

    l7Scene.value.addLayer(lineLayer);
    console.log("[Map] Line слой добавлен");
  }

  // Point слой (для CircleMarker)
  const pointData = objectsArray
    .filter((obj) => obj.type === "CircleMarker")
    .map((obj) => ({
      id: obj.id,
      coordinates: obj.coordinates[0],
      fillColor: obj.style.fillColor ?? [0, 255, 0, 255],
      radius: 15,
    }));

  console.log("[Map] Point данные:", pointData.length, "объектов");
  if (pointData.length > 0) {
    console.log("[Map] Первая точка:", pointData[0]);
  }

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
      .active(true)
      .style({
        opacity: 1,
      });

    // Добавляем обработчик клика на слой
    pointLayer.on("click", (e: any) => {
      console.log("[Map] Point layer click:", e);
      if (e.feature?.properties?.id) {
        selectObject(e.feature.properties.id);
      }
    });

    l7Scene.value.addLayer(pointLayer);
    console.log("[Map] Point слой добавлен");
  }

  console.log("[Map] createLayers завершён");
};

// Инициализация карты
onMounted(async () => {
  // L7 создаст свою карту MapLibre внутри сцены
  try {
    const l7Map = new MapLibre({
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
            attribution:
              '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
          },
        },
        layers: [
          {
            id: "osm-layer",
            type: "raster",
            source: "osm",
          },
        ],
      },
      center: [103.888249, 52.544358],
      zoom: 14,
      rotation: 0,
      pitch: 0,
    });

    l7Scene.value = new Scene({
      id: "map",
      map: l7Map,
    });

    // Ждём инициализации сцены
    l7Scene.value.on("loaded", () => {
      console.log("[Map] L7 Scene загружена");

      // Сохраняем экземпляр MapLibre
      mapInstance.value = (l7Map as any).map;

      // Добавляем обработчик клика на MapLibre
      mapInstance.value.on("click", onMapClick);

      // Применяем стили для курсоров
      setTimeout(() => {
        const mapContainer = document.getElementById("map");
        if (mapContainer) {
          const canvas = mapContainer.querySelector(".maplibregl-canvas");
          if (canvas) {
            (canvas as HTMLCanvasElement).style.cursor = plusCursor.value;
          }
        }
      }, 100);

      createLayers();
    });

    // Добавляем обработчик клика на L7 сцену после создания
    setTimeout(() => {
      if (l7Scene.value) {
        l7Scene.value.on("click", (e: any) => {
          console.log("[Map] L7 click event:", e);
          if (e.lngLat) {
            const lngLat: LngLatTuple = [e.lngLat.lng, e.lngLat.lat];
            console.log("[Map] Клик через L7:", lngLat);
            handleMapClick(lngLat);
          }
        });
      }
    }, 500);
  } catch (error) {
    console.error("[Map] Ошибка инициализации L7 Scene:", error);
  }
});

// Watch для реактивности
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

/* L7 canvas container - пропускаем события к карте */
:deep(.l7-canvas-container),
:deep(.l7-scene) {
  pointer-events: none !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  z-index: 10 !important;
}

/* Но сами canvas элементы L7 должны получать события для интерактивности слоёв */
:deep(.l7-canvas-container canvas),
:deep(.l7-scene canvas) {
  pointer-events: auto !important;
}

/* Курсоры для MapLibre canvas */
:deep(.maplibregl-canvas) {
  cursor: v-bind(plusCursor) !important;
}

:deep(.maplibregl-canvas:active) {
  cursor: v-bind(grabCursor) !important;
}

/* Курсор для контейнера карты */
:deep(#map) {
  cursor: v-bind(plusCursor);
}

:deep(#map:active) {
  cursor: v-bind(grabCursor);
}
</style>
