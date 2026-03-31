<script setup lang="ts">
import { Map } from '@/components/Map';
import { useMapObjectStore } from '@/store';
import { useTilesStore } from '@/store/useTilesStore';
import { onMounted, onUnmounted, ref } from 'vue';
import { Loader } from 'lucide-vue-next';

const objectStore = useMapObjectStore();
const loading = ref(true);

const loadObjects = async () => {
  console.log('[MapOnly] Loading objects from DB');
  await objectStore.loadAllObjectsFromDB();
  loading.value = false;
};

// Обработчик синхронизации между окнами
const handlePanelSync = async (event: CustomEvent) => {
  console.log('[MapOnly] Panel sync event:', event.detail);
  const { type, data } = event.detail;

  if (type === 'OBJECT_DELETED' && data?.id) {
    objectStore.deleteObject(data.id);
  } else if (type === 'OBJECT_CREATED' || type === 'OBJECT_UPDATED') {
    await loadObjects();
    console.log('[MapOnly] Objects reloaded after', type);
  }

  if (type === 'TILE_LAYER_CHANGED' && data?.layer) {
    const tilesStore = useTilesStore();
    if (tilesStore.currentLayer !== data.layer) {
      tilesStore.setLayer(data.layer as typeof tilesStore.currentLayer);
      console.log('[MapOnly] Tile layer changed to:', data.layer);
    }
  }
};

// Обработчик изменения выбранного типа
const handleChosenTypeChanged = (event: CustomEvent) => {
  console.log('[MapOnly] Chosen type changed:', event.detail);
  const { option } = event.detail.data;
  if (option && Array.isArray(option) && option.length === 2) {
    objectStore.$state.ChosenObjectType = option as unknown as typeof objectStore.$state.ChosenObjectType;
  }
};

onMounted(() => {
  // Слушаем события синхронизации
  globalThis.addEventListener('panel-sync', handlePanelSync as unknown as EventListener);
  globalThis.addEventListener('chosen-type-changed', handleChosenTypeChanged as unknown as EventListener);

  // Загружаем объекты сразу
  loadObjects();
});

onUnmounted(() => {
  globalThis.removeEventListener('panel-sync', handlePanelSync as unknown as EventListener);
  globalThis.removeEventListener('chosen-type-changed', handleChosenTypeChanged as unknown as EventListener);
});
</script>

<template>
  <div class="h-screen w-screen overflow-hidden relative">
    <Map />
    
    <!-- Спиннер загрузки -->
    <div v-if="loading" class="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="flex flex-col items-center gap-4">
        <Loader class="w-12 h-12 animate-spin text-primary" />
        <p class="text-lg font-medium text-foreground">Загрузка карты...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
#map {
  height: 100%;
  width: 100%;
}
</style>
