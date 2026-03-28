<script setup lang="ts">
import MapPanel from "@/components/MapPanel/MapPanel.vue";
import { useMapObjectStore } from "@/store";
import { usePanelLayoutStore } from "@/store/usePanelLayoutStore";
import { onMounted, onUnmounted } from "vue";

const objectStore = useMapObjectStore();
const layoutStore = usePanelLayoutStore();

const pyWebViewReadyHandler = async () => {
  console.log('[Main] pywebview ready - loading objects from DB');
  await objectStore.loadAllObjectsFromDB();
  globalThis.removeEventListener("pywebviewready", pyWebViewReadyHandler);
};

// Обработчик синхронизации между окнами
const handlePanelSync = async (event: CustomEvent) => {
  console.log('[Main] Panel sync event:', event.detail);
  const { type } = event.detail;
  
  if (type === 'OBJECT_CREATED' || type === 'OBJECT_UPDATED' || type === 'OBJECT_DELETED') {
    // Перезагружаем объекты из БД
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
  globalThis.addEventListener('panel-sync', handlePanelSync as EventListener);
  
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

onUnmounted(() => {
  globalThis.removeEventListener("pywebviewready", pyWebViewReadyHandler);
  globalThis.removeEventListener('panel-sync', handlePanelSync as EventListener);
});
</script>

<template>
  <MapPanel />
</template>

<style scoped></style>
