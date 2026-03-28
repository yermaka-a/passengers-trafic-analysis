<script lang="ts" setup>
import { Map } from "@/components/Map";
import { List } from "@/components/List";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import BrushTable from "@/components/BrushTable/BrushTable.vue";
import { Button } from "@/components/ui/button";
import { usePanelLayoutStore } from "@/store/usePanelLayoutStore";

const layoutStore = usePanelLayoutStore();

// Обработчики для кнопок
const handleOpenWindow = async (panelId: string) => {
  // Проверяем, доступен ли pywebview API
  if ((window as any).pywebview?.api?.open_panel_window) {
    try {
      await (window as any).pywebview.api.open_panel_window(panelId);
    } catch (e) {
      console.error('[MapPanel] Error opening panel:', e);
      // Fallback: открываем в новом окне браузера
      fallbackOpenWindow(panelId);
    }
  } else {
    // pywebview недоступен, открываем в браузере
    fallbackOpenWindow(panelId);
  }
};

const fallbackOpenWindow = (panelId: string) => {
  const url = `${window.location.origin}?panel=${panelId}`;
  const features = 'width=1000,height=700,menubar=no,toolbar=no';
  window.open(url, `panel-${panelId}`, features);
};

const handleCloseWindow = (panelId: string) => {
  layoutStore.closeFloatingPanel(panelId);
};
</script>

<template>
  <ResizablePanelGroup
    direction="horizontal"
    class="max-w-dvw min-h-[95vh] rounded-lg border mt-1"
  >
    <!-- Левая панель с BrushTable и List -->
    <ResizablePanel :default-size="50">
      <ResizablePanelGroup direction="vertical">
        <!-- BrushTable -->
        <ResizablePanel :default-size="25">
          <div class="relative h-full">
            <BrushTable />
            <Button
              variant="outline"
              size="sm"
              class="absolute top-2 right-2 h-7 px-2 text-xs opacity-50 hover:opacity-100"
              @click="handleOpenWindow('brushTable')"
              title="Открыть в отдельном окне"
            >
              📤
            </Button>
          </div>
        </ResizablePanel>
        
        <ResizableHandle withHandle />
        
        <!-- List -->
        <ResizablePanel :default-size="75">
          <div class="relative h-full">
            <List />
            <Button
              variant="outline"
              size="sm"
              class="absolute top-2 right-2 h-7 px-2 text-xs opacity-50 hover:opacity-100"
              @click="handleOpenWindow('list')"
              title="Открыть в отдельном окне"
            >
              📤
            </Button>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </ResizablePanel>

    <ResizableHandle withHandle />

    <!-- Map панель -->
    <ResizablePanel :default-size="100">
      <div class="relative h-full">
        <Map />
        <Button
          variant="outline"
          size="sm"
          class="absolute top-2 right-2 h-7 px-2 text-xs opacity-50 hover:opacity-100"
          @click="handleOpenWindow('map')"
          title="Открыть в отдельном окне"
        >
          📤
        </Button>
      </div>
    </ResizablePanel>
  </ResizablePanelGroup>
</template>

<style scoped></style>
