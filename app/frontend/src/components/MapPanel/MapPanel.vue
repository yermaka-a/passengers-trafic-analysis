<script lang="ts" setup>
import { Map } from "@/components/Map";
import { List } from "@/components/List";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Button } from "@/components/ui/button";
import BrushTable from "@/components/BrushTable/BrushTable.vue";
import LayoutMenu from "@/components/LayoutMenu/LayoutMenu.vue";
import { useLayoutStore } from "@/store/useLayoutStore";

const layoutStore = useLayoutStore();
const layout = layoutStore.layout;

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
  <div class="flex flex-col h-screen w-screen">
    <!-- Toolbar с кнопками управления -->
    <div class="flex justify-between items-center p-2 border-b bg-gray-50">
      <LayoutMenu />
      <div class="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          class="cursor-pointer"
          @click="handleOpenWindow('map')"
          title="Открыть карту в отдельном окне"
        >
          📤 Карта
        </Button>
        <Button
          variant="outline"
          size="sm"
          class="cursor-pointer"
          @click="handleOpenWindow('list')"
          title="Открыть список в отдельном окне"
        >
          📤 Список
        </Button>
        <Button
          variant="outline"
          size="sm"
          class="cursor-pointer"
          @click="handleOpenWindow('brushTable')"
          title="Открыть инструменты в отдельном окне"
        >
          📤 Инструменты
        </Button>
      </div>
    </div>

    <!-- Main Layout -->
    <ResizablePanelGroup
      :direction="layout.orientation"
      class="flex-1 h-full"
    >
      <!-- Карта слева/справа -->
      <template v-if="layout.mapPosition === 'left' || layout.mapPosition === 'right'">
        <ResizablePanel :default-size="layout.mapSize" :min-size="20">
          <div class="relative h-full">
            <Map />
          </div>
        </ResizablePanel>
        
        <ResizableHandle withHandle />
        
        <!-- Левая панель с BrushTable и List -->
        <ResizablePanel :default-size="100 - layout.mapSize" :min-size="20">
          <ResizablePanelGroup :direction="layout.leftOrientation">
            <ResizablePanel :default-size="layout.brushSize" :min-size="15">
              <div class="relative h-full">
                <BrushTable />
              </div>
            </ResizablePanel>
            
            <ResizableHandle withHandle />
            
            <ResizablePanel :default-size="layout.listSize" :min-size="15">
              <div class="relative h-full">
                <List />
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </ResizablePanel>
      </template>
      
      <!-- Карта сверху/снизу -->
      <template v-else-if="layout.mapPosition === 'top' || layout.mapPosition === 'bottom'">
        <!-- BrushTable и List -->
        <ResizablePanel :default-size="100 - layout.mapSize" :min-size="20">
          <ResizablePanelGroup :direction="layout.leftOrientation">
            <ResizablePanel :default-size="layout.brushSize" :min-size="15">
              <div class="relative h-full">
                <BrushTable />
              </div>
            </ResizablePanel>
            
            <ResizableHandle withHandle />
            
            <ResizablePanel :default-size="layout.listSize" :min-size="15">
              <div class="relative h-full">
                <List />
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </ResizablePanel>
        
        <ResizableHandle withHandle />
        
        <ResizablePanel :default-size="layout.mapSize" :min-size="20">
          <div class="relative h-full">
            <Map />
          </div>
        </ResizablePanel>
      </template>
    </ResizablePanelGroup>
  </div>
</template>

<style scoped>
/* Адаптивные размеры для панелей */
.resizable-panel {
  min-height: 200px;
  min-width: 300px;
}
</style>
