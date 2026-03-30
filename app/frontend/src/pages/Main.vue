<script setup lang="ts">
import MapPanel from "@/components/MapPanel/MapPanel.vue";
import { useMapObjectStore } from "@/store";
import { usePanelLayoutStore } from "@/store/usePanelLayoutStore";
import { useTilesStore } from "@/store/useTilesStore";
import { onMounted, onUnmounted } from "vue";

const objectStore = useMapObjectStore();
const layoutStore = usePanelLayoutStore();
const tilesStore = useTilesStore();

const pyWebViewReadyHandler = async () => {
  console.log('[Main] pywebview ready - loading objects from DB');
  await objectStore.loadAllObjectsFromDB();
  
  // Загружаем сохранённый слой карт через useApi
  const useApiModule = await import('@/composables/useApi');
  const { getCurrentTileLayer } = useApiModule.default();
  try {
    const result = await getCurrentTileLayer();
    if (result?.status === 'success' && result?.layer) {
      tilesStore.setLayer(result.layer as typeof tilesStore.currentLayer);
    }
  } catch (e) {
    console.error('[Main] Error loading tile layer:', e);
  }
  
  globalThis.removeEventListener("pywebviewready", pyWebViewReadyHandler);
};

// Обработчик синхронизации между окнами
const handlePanelSync = async (event: CustomEvent) => {
  console.log('[Main] Panel sync event:', event.detail);
  const { type, data } = event.detail;

  if (type === 'OBJECT_DELETED' && data?.id) {
    // Просто удаляем объект из store, без полной перезагрузки
    console.log('[Main] Deleting object from store:', data.id);
    objectStore.deleteObject(data.id);
    console.log('[Main] Object deleted, remaining:', objectStore.Objects.size);
  } else if (type === 'OBJECT_CREATED' || type === 'OBJECT_UPDATED') {
    // Для создания/обновления - полная перезагрузка
    await objectStore.loadAllObjectsFromDB();
    console.log('[Main] Objects reloaded after', type);
  }
};

onMounted(async () => {
  // Проверка на режим отдельной панели
  const urlParams = new URLSearchParams(window.location.search);
  const panelId = urlParams.get("panel");
  
  if (panelId) {
    // Режим отдельного окна - показываем только одну панель
    layoutStore.showOnlyPanel(panelId);
    document.title = `Panel: ${panelId}`;
  }
  
  // Слушаем события синхронизации
  globalThis.addEventListener('panel-sync', handlePanelSync as unknown as EventListener);

  // Слушаем изменения выбранного типа (для синхронизации BrushTable)
  globalThis.addEventListener('chosen-type-changed', handleChosenTypeChanged as unknown as EventListener);

  // Проверяем готовность pywebview
  if ((globalThis as any).pywebview?.api) {
    // pywebview уже готов (для отдельных окон)
    await pyWebViewReadyHandler();
  } else {
    // Ждём события pywebviewready (для главного окна)
    console.log('[Main] Waiting for pywebviewready event...');
    globalThis.addEventListener("pywebviewready", pyWebViewReadyHandler);
  }
});

// Обработчик изменения выбранного типа
const handleChosenTypeChanged = (event: CustomEvent) => {
  console.log('[Main] Chosen type changed:', event.detail);
  const { option } = event.detail.data;
  if (option && Array.isArray(option) && option.length === 2) {
    // Обновляем store напрямую без вызова Python API
    objectStore.$state.ChosenObjectType = option as unknown as typeof objectStore.$state.ChosenObjectType;
  }
};

onUnmounted(() => {
  globalThis.removeEventListener("pywebviewready", pyWebViewReadyHandler);
  globalThis.removeEventListener('panel-sync', handlePanelSync as unknown as EventListener);
  globalThis.removeEventListener('chosen-type-changed', handleChosenTypeChanged as unknown as EventListener);
});
</script>

<template>
  <MapPanel />
</template>

<style scoped></style>
