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

// Обработчики для кнопок
const handleOpenWindow = async (panelId: string) => {
  // Проверяем, доступен ли pywebview API
  if ((window as any).pywebview?.api?.open_panel_window) {
    try {
      const result = await (window as any).pywebview.api.open_panel_window(panelId);
      console.log('[MapPanel] Panel opened:', result);
    } catch (e) {
      console.error('[MapPanel] Error opening panel:', e);
      alert('Ошибка открытия окна. Проверьте консоль.');
    }
  } else {
    // pywebview недоступен - показываем ошибку
    alert('Откройте приложение через python main.py для работы с окнами');
  }
};
</script>

<template>
  <ResizablePanelGroup
    direction="horizontal"
    class="max-w-dvw min-h-[95vh] rounded-lg border mt-1"
  >
    <!-- Левая панель с BrushTable и List -->
    <ResizablePanel :default-size="40">
      <ResizablePanelGroup direction="vertical">
        <!-- BrushTable -->
        <ResizablePanel :default-size="30">
          <div class="relative h-full">
            <BrushTable />
            <Button
              variant="outline"
              size="sm"
              class="absolute top-2 right-2 h-7 px-2 text-xs opacity-50 hover:opacity-100"
              @click="handleOpenWindow('brushTable')"
              title="Открыть в отдельном окне pywebview"
            >
              📤
            </Button>
          </div>
        </ResizablePanel>
        
        <ResizableHandle withHandle />
        
        <!-- List -->
        <ResizablePanel :default-size="70">
          <div class="relative h-full">
            <List />
            <Button
              variant="outline"
              size="sm"
              class="absolute top-2 right-2 h-7 px-2 text-xs opacity-50 hover:opacity-100"
              @click="handleOpenWindow('list')"
              title="Открыть в отдельном окне pywebview"
            >
              📤
            </Button>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </ResizablePanel>

    <ResizableHandle withHandle />

    <!-- Map панель -->
    <ResizablePanel :default-size="60">
      <div class="relative h-full">
        <Map />
        <Button
          variant="outline"
          size="sm"
          class="absolute top-2 right-2 h-7 px-2 text-xs opacity-50 hover:opacity-100"
          @click="handleOpenWindow('map')"
          title="Открыть в отдельном окне pywebview"
        >
          📤
        </Button>
      </div>
    </ResizablePanel>
  </ResizablePanelGroup>
</template>

<style scoped></style>
