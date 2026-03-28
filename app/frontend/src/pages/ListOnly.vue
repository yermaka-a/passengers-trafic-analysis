<script setup lang="ts">
import { List } from '@/components/List';
import { useMapObjectStore } from '@/store';
import { onMounted } from 'vue';

const objectStore = useMapObjectStore();

const pyWebViewReadyHandler = async () => {
  console.log('[ListOnly] pywebview ready - loading objects from DB');
  await objectStore.loadAllObjectsFromDB();
  globalThis.removeEventListener('pywebviewready', pyWebViewReadyHandler);
};

onMounted(() => {
  // Слушаем события синхронизации
  globalThis.addEventListener('panel-sync', handlePanelSync as EventListener);
  
  // Инициализация pywebview
  if ((globalThis as any)?.pywebview?.api?.objects) {
    pyWebViewReadyHandler();
  } else {
    globalThis.addEventListener('pywebviewready', pyWebViewReadyHandler);
  }
});

// Обработчик синхронизации между окнами
const handlePanelSync = async (event: CustomEvent) => {
  console.log('[ListOnly] Panel sync event:', event.detail);
  const { type } = event.detail;
  
  if (type === 'OBJECT_CREATED' || type === 'OBJECT_UPDATED' || type === 'OBJECT_DELETED') {
    await objectStore.loadAllObjectsFromDB();
    console.log('[ListOnly] Objects reloaded after', type);
  }
};
</script>

<template>
  <div class="h-screen w-screen overflow-hidden">
    <List />
  </div>
</template>

<style scoped>
/* List занимает весь экран */
</style>
