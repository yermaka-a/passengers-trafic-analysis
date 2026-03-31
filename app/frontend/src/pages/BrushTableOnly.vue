<script setup lang="ts">
import BrushTable from '@/components/BrushTable/BrushTable.vue';
import { useMapObjectStore } from '@/store';
import { onMounted, onUnmounted, ref } from 'vue';
import { Loader } from 'lucide-vue-next';

const objectStore = useMapObjectStore();
const loading = ref(true);

const loadObjects = async () => {
  console.log('[BrushTableOnly] Loading objects from DB');
  await objectStore.loadAllObjectsFromDB();
  loading.value = false;
};

const pyWebViewReadyHandler = async () => {
  console.log('[BrushTableOnly] pywebview ready - loading objects from DB');
  await loadObjects();
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
  <div class="h-screen w-screen overflow-hidden p-4 relative">
    <BrushTable />
    
    <!-- Спиннер загрузки -->
    <div v-if="loading" class="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="flex flex-col items-center gap-4">
        <Loader class="w-12 h-12 animate-spin text-primary" />
        <p class="text-lg font-medium text-foreground">Загрузка инструментов...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* BrushTable занимает весь экран с отступом */
</style>
