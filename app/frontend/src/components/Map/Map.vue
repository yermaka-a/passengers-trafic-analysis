<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive, computed } from "vue";
import "leaflet/dist/leaflet.css";
import { storeToRefs } from "pinia";
import { LeafletMapConfig } from "@/config";
import { useMapStore, useTilesStore } from "@/store";
import * as L from "leaflet";
import {
  ObjectEditor,
  useMapObjectStore,
  type Objects,
} from "@/store/useMapObjectStore";
import MapOptions from "./MapOptions.vue";
import PlusCursor from "@/assets/plus-cursor.svg";
import GrabCursor from "@/assets/grab-cursor.svg";
const plusCursor = computed(() => `url("${PlusCursor}") 16 16, auto`);
const grabCursor = computed(() => `url("${GrabCursor}") 16 16, auto`);
const mapObjectStore = useMapObjectStore();
const mapStore = useMapStore();
const { mapInstance } = storeToRefs(mapStore);
const { MapObject, ObjectsCount } = storeToRefs(mapObjectStore);
const tilesStore = useTilesStore();
// 0-удалить, 1-добавить
let EventsHistory = reactive<L.LatLng[]>([]);
const EventNumber = ref<number>(0);
const prevAction = () => {
  if (EventsHistory.length > 0 && EventNumber.value !== 0) {
    let coords = null;
    switch (true) {
      case MapObject.value instanceof L.Polygon:
        coords = MapObject.value.getLatLngs();
        (coords[0] as L.LatLng[]).splice(-1, 1);
        console.log(coords);
        MapObject.value.redraw();
        break;
      case MapObject.value instanceof L.Polyline:
        coords = MapObject.value.getLatLngs();
        (coords as L.LatLng[]).splice(-1, 1);
        MapObject.value.redraw();
        break;
      case MapObject.value instanceof L.CircleMarker:
        MapObject.value.removeFrom(mapInstance.value as L.Map);
        break;
    }
    EventNumber.value--;
  }
};
const nextAction = () => {
  if (EventsHistory.length > 0 && EventNumber.value !== EventsHistory.length) {
    EventNumber.value++;
    const event = EventsHistory[EventNumber.value - 1];

    switch (true) {
      case MapObject.value instanceof L.Polygon:
        MapObject.value.addLatLng([
          event?.lat,
          event?.lng,
        ] as L.LatLngExpression);
        MapObject.value.redraw();
        break;
      case MapObject.value instanceof L.Polyline:
        MapObject.value.addLatLng([
          event?.lat,
          event?.lng,
        ] as L.LatLngExpression);
        MapObject.value.redraw();
        break;
      case MapObject.value instanceof L.CircleMarker:
        MapObject.value.setLatLng([
          event?.lat,
          event?.lng,
        ] as L.LatLngExpression);
        break;
    }
  }
};
const cancelChanges = () => {
  if (MapObject.value instanceof ObjectEditor) return;
  const Map = mapInstance.value as L.Map;
  if (mapInstance && MapObject.value) MapObject.value?.removeFrom(Map);
  MapObject.value = null;
  EventsHistory.length = 0;
  ObjectsCount.value--;
};
const submitChanges = async () => {
  if (mapInstance && MapObject.value) {
    if (MapObject.value instanceof ObjectEditor) return;
    await mapObjectStore.setObject(MapObject.value as Objects);
    MapObject.value = null;
  }
};

const AddPolygonClickHandler = async (e: L.LeafletMouseEvent) => {
  e.originalEvent.preventDefault();
  if (!MapObject.value) {
    MapObject.value = mapObjectStore.getObjectByChosenType();
  }
  if (MapObject.value instanceof ObjectEditor) return;
  const Map = mapInstance.value as L.Map;
  switch (true) {
    case MapObject.value instanceof L.Polygon ||
      MapObject.value instanceof L.Polyline:
      MapObject.value.addLatLng(e.latlng);

      break;
    case MapObject.value instanceof L.CircleMarker:
      MapObject.value.setLatLng(e.latlng);
      MapObject.value.bringToFront();
      break;
  }
  if (EventsHistory.length !== EventNumber.value) {
    EventsHistory.splice(EventNumber.value);
    EventsHistory.push(e.latlng);
    MapObject.value.addTo(Map);
    EventNumber.value = EventsHistory.length;
    return;
  }
  EventsHistory.push(e.latlng);
  MapObject.value.addTo(Map);
  EventNumber.value++;
};
onMounted(() => {
  mapStore.initMap("map");

  if (mapInstance.value) {
    L.control
      .attribution({
        position: "topleft",
        prefix: "leaflet",
      })
      .addTo(mapInstance.value);
    L.tileLayer(tilesStore.$state.OSM.TilesURL, {
      attribution: LeafletMapConfig.OSMAttr,
    }).addTo(mapInstance.value);
  } else {
    console.error("Map component unregistred ref");
  }

  mapInstance?.value?.on("click", AddPolygonClickHandler);
});

onUnmounted(() => {
  mapInstance?.value?.off("click", AddPolygonClickHandler);
});
</script>

<template>
  <MapOptions
    :cancel-changes="cancelChanges"
    :submit-changes="submitChanges"
    :prev-action="prevAction"
    :next-action="nextAction"
  />
  <div class="flex-1 h-screen overflow-scroll">
    <div id="map"></div>
  </div>
</template>

<style scoped>
:deep(#map) {
  height: 100vh;
  width: 100vw;
  outline: none;
  user-select: none;
  cursor: v-bind(plusCursor);
}

:deep(.leaflet-drag-target) {
  cursor: v-bind(grabCursor) !important;
}
</style>
