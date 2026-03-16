<script setup lang="ts">
import { useTilesStore } from "@/store/useTilesStore";
import { useMapStore } from "@/store/useMapStore";
import type { TileLayer } from "@/store/useTilesStore";

const tilesStore = useTilesStore();
const mapStore = useMapStore();

const switchLayer = (layer: TileLayer) => {
  tilesStore.setLayer(layer);

  if (mapStore.mapInstance) {
    const currentLayer = tilesStore.getCurrentLayerConfig();

    // Получаем текущий стиль и обновляем источник тайлов
    const style = mapStore.mapInstance.getStyle();

    if (style.sources?.["osm"]) {
      // Обновляем тайлы и атрибуцию
      style.sources["osm"].tiles = currentLayer.tiles;
      style.sources["osm"].attribution = currentLayer.attribution;

      // Применяем обновлённый стиль
      mapStore.mapInstance.setStyle(style);
    }
  }
};
</script>

<template>
  <div class="tiles-switcher flex gap-2 p-2 bg-white rounded shadow-md">
    <button
      v-for="(layer, key) in tilesStore.layers"
      :key="key"
      @click="switchLayer(key as TileLayer)"
      :class="[
        'px-3 py-1.5 rounded text-sm font-medium transition-colors',
        tilesStore.currentLayer === key
          ? 'bg-blue-500 text-white'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      ]"
    >
      {{ layer.name }}
    </button>
  </div>
</template>

<style scoped>
.tiles-switcher {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
}
</style>
