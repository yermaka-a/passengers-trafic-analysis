<script setup lang="ts">
import MapPanel from "@/components/MapPanel/MapPanel.vue";
import { useMapObjectStore } from "@/store";
import { usePanelLayoutStore } from "@/store/usePanelLayoutStore";
import { onMounted, onUnmounted } from "vue";

const objectStore = useMapObjectStore();
const layoutStore = usePanelLayoutStore();

const pyWebViewReadyHandler = async () => {
  await objectStore.loadAllObjectsFromDB();
  globalThis.removeEventListener("pywebviewready", pyWebViewReadyHandler);
};

onMounted(async () => {
  // Инициализация layout
  layoutStore.initLayout();
  
  // Проверка на режим отдельной панели
  const urlParams = new URLSearchParams(window.location.search);
  const panelId = urlParams.get("panel");
  
  if (panelId) {
    // Режим отдельного окна - показываем только одну панель
    layoutStore.showOnlyPanel(panelId);
    document.title = `Panel: ${panelId}`;
  }
  
  // Инициализация pywebview
  if ((globalThis as any)?.pywebview?.api?.objects) {
    await pyWebViewReadyHandler();
  } else {
    globalThis.addEventListener("pywebviewready", pyWebViewReadyHandler);
  }
});

onUnmounted(() => {
  globalThis.removeEventListener("pywebviewready", pyWebViewReadyHandler);
});
</script>

<template>
  <MapPanel />
</template>

<style scoped></style>
