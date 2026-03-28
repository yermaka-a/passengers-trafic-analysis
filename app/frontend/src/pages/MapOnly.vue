<script setup lang="ts">
import { Map } from '@/components/Map';
import { useMapObjectStore } from '@/store';
import { useTilesStore } from '@/store/useTilesStore';
import { onMounted, onUnmounted } from 'vue';

const objectStore = useMapObjectStore();

const pyWebViewReadyHandler = async () => {
  console.log('[MapOnly] pywebview ready - loading objects from DB');
  await objectStore.loadAllObjectsFromDB();
  globalThis.removeEventListener('pywebviewready', pyWebViewReadyHandler);
};

// Обработчик синхронизации между окнами
const handlePanelSync = async (event: CustomEvent) => {
  console.log('[MapOnly] Panel sync event:', event.detail);
  const { type, data } = event.detail;

  if (type === 'OBJECT_CREATED' || type === 'OBJECT_UPDATED' || type === 'OBJECT_DELETED') {
    await objectStore.loadAllObjectsFromDB();
    console.log('[MapOnly] Objects reloaded after', type);
  }
  
  if (type === 'TILE_LAYER_CHANGED' && data?.layer) {
    const tilesStore = useTilesStore();
    if (tilesStore.currentLayer !== data.layer) {
      tilesStore.setLayer(data.layer as typeof tilesStore.currentLayer);
      console.log('[MapOnly] Tile layer changed to:', data.layer);
      // Применяем слой - карта обновится через watch
    }
  }
};

// Обработчик изменения выбранного типа
const handleChosenTypeChanged = (event: CustomEvent) => {
  console.log('[MapOnly] Chosen type changed:', event.detail);
  const { option } = event.detail.data;
  if (option && Array.isArray(option) && option.length === 2) {
    // Обновляем store напрямую без вызова Python API
    objectStore.$state.ChosenObjectType = option as unknown as typeof objectStore.$state.ChosenObjectType;
  }
};

onMounted(() => {
  // Слушаем события синхронизации
  globalThis.addEventListener('panel-sync', handlePanelSync as unknown as EventListener);
  globalThis.addEventListener('chosen-type-changed', handleChosenTypeChanged as unknown as EventListener);

  // Инициализация pywebview
  if ((globalThis as any)?.pywebview?.api?.objects) {
    pyWebViewReadyHandler();
  } else {
    globalThis.addEventListener('pywebviewready', pyWebViewReadyHandler);
  }
});

onUnmounted(() => {
  globalThis.removeEventListener('pywebviewready', pyWebViewReadyHandler);
  globalThis.removeEventListener('panel-sync', handlePanelSync as unknown as EventListener);
  globalThis.removeEventListener('chosen-type-changed', handleChosenTypeChanged as unknown as EventListener);
});
</script>

<template>
  <div class="h-screen w-screen overflow-hidden">
    <Map />
  </div>
</template>

<style scoped>
#map {
  height: 100%;
  width: 100%;
}
</style>
