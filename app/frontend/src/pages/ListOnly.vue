<script setup lang="ts">
import { List } from '@/components/List';
import { useMapObjectStore } from '@/store';
import { onMounted, onUnmounted } from 'vue';

const objectStore = useMapObjectStore();

const pyWebViewReadyHandler = async () => {
  console.log('[ListOnly] pywebview ready - loading objects from DB');
  await objectStore.loadAllObjectsFromDB();
  globalThis.removeEventListener('pywebviewready', pyWebViewReadyHandler);
};

// Обработчик синхронизации между окнами
const handlePanelSync = async (event: CustomEvent) => {
  console.log('[ListOnly] Panel sync event:', event.detail);
  const { type } = event.detail;
  
  if (type === 'OBJECT_CREATED' || type === 'OBJECT_UPDATED' || type === 'OBJECT_DELETED') {
    await objectStore.loadAllObjectsFromDB();
    console.log('[ListOnly] Objects reloaded after', type);
  }
};

// Обработчик изменения выбранного типа
const handleChosenTypeChanged = (event: CustomEvent) => {
  console.log('[ListOnly] Chosen type changed:', event.detail);
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
    <List />
  </div>
</template>

<style scoped>
/* List занимает весь экран */
</style>
