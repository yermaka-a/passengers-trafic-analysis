<script setup lang="ts">
import BrushTable from '@/components/BrushTable/BrushTable.vue';
import { useMapObjectStore } from '@/store';
import { onMounted, onUnmounted } from 'vue';

const objectStore = useMapObjectStore();

const pyWebViewReadyHandler = async () => {
  console.log('[BrushTableOnly] pywebview ready - loading objects from DB');
  await objectStore.loadAllObjectsFromDB();
  globalThis.removeEventListener('pywebviewready', pyWebViewReadyHandler);
};

// Обработчик синхронизации между окнами
const handlePanelSync = async (event: CustomEvent) => {
  console.log('[BrushTableOnly] Panel sync event:', event.detail);
  const { type } = event.detail;
  
  if (type === 'OBJECT_CREATED' || type === 'OBJECT_UPDATED' || type === 'OBJECT_DELETED') {
    await objectStore.loadAllObjectsFromDB();
    console.log('[BrushTableOnly] Objects reloaded after', type);
  }
};

// Обработчик изменения выбранного типа
const handleChosenTypeChanged = (event: CustomEvent) => {
  console.log('[BrushTableOnly] Chosen type changed:', event.detail);
  const { option } = event.detail.data;
  if (option && Array.isArray(option) && option.length === 2) {
    // Обновляем store напрямую без вызова Python API
    objectStore.$state.ChosenObjectType = option as typeof objectStore.$state.ChosenObjectType;
  }
};

onMounted(() => {
  // Слушаем события синхронизации
  globalThis.addEventListener('panel-sync', handlePanelSync as EventListener);
  globalThis.addEventListener('chosen-type-changed', handleChosenTypeChanged as EventListener);

  // Инициализация pywebview
  if ((globalThis as any)?.pywebview?.api?.objects) {
    pyWebViewReadyHandler();
  } else {
    globalThis.addEventListener('pywebviewready', pyWebViewReadyHandler);
  }
});

onUnmounted(() => {
  globalThis.removeEventListener('pywebviewready', pyWebViewReadyHandler);
  globalThis.removeEventListener('panel-sync', handlePanelSync as EventListener);
  globalThis.removeEventListener('chosen-type-changed', handleChosenTypeChanged as EventListener);
});
</script>

<template>
  <div class="h-screen w-screen overflow-hidden p-4">
    <BrushTable />
  </div>
</template>

<style scoped>
/* BrushTable занимает весь экран с отступом */
</style>
