<script setup lang="ts">
import MapPanel from "@/components/MapPanel/MapPanel.vue";
import { useMapObjectStore } from "@/store";
import { onMounted, onUnmounted } from "vue";
const objectStore = useMapObjectStore();

const pyWebViewReadyHandler = async () => {
  await objectStore.loadAllObjectsFromDB();
  globalThis.removeEventListener("pywebviewready", pyWebViewReadyHandler);
};

onMounted(async () => {
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
