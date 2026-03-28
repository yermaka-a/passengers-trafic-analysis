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
  if ((window as any).pywebview?.api?.open_panel_window) {
    try {
      const result = await (window as any).pywebview.api.open_panel_window(panelId);
      console.log('[MapPanel] Panel opened:', result);
    } catch (e) {
      console.error('[MapPanel] Error opening panel:', e);
      alert('Ошибка открытия окна. Проверьте консоль.');
    }
  } else {
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

    <!-- Main Layout: Карта сверху -->
    <ResizablePanelGroup
      v-if="layout.mapPosition === 'top'"
      direction="vertical"
      class="flex-1 h-full"
    >
      <ResizablePanel :default-size="layout.mapSize" :min-size="0" :max-size="100">
        <div class="relative h-full">
          <Map />
        </div>
      </ResizablePanel>
      
      <ResizableHandle withHandle />
      
      <ResizablePanel :default-size="100 - layout.mapSize" :min-size="0" :max-size="100">
        <ResizablePanelGroup direction="horizontal">
          <ResizablePanel :default-size="layout.toolsSize" :min-size="0" :max-size="100">
            <div class="relative h-full">
              <BrushTable />
            </div>
          </ResizablePanel>
          
          <ResizableHandle withHandle />
          
          <ResizablePanel :default-size="100 - layout.toolsSize" :min-size="0" :max-size="100">
            <div class="relative h-full">
              <List />
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </ResizablePanel>
    </ResizablePanelGroup>

    <!-- Main Layout: Карта снизу -->
    <ResizablePanelGroup
      v-else-if="layout.mapPosition === 'bottom'"
      direction="vertical"
      class="flex-1 h-full"
    >
      <ResizablePanel :default-size="100 - layout.mapSize" :min-size="0" :max-size="100">
        <ResizablePanelGroup direction="horizontal">
          <ResizablePanel :default-size="layout.toolsSize" :min-size="0" :max-size="100">
            <div class="relative h-full">
              <BrushTable />
            </div>
          </ResizablePanel>
          
          <ResizableHandle withHandle />
          
          <ResizablePanel :default-size="100 - layout.toolsSize" :min-size="0" :max-size="100">
            <div class="relative h-full">
              <List />
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </ResizablePanel>
      
      <ResizableHandle withHandle />
      
      <ResizablePanel :default-size="layout.mapSize" :min-size="0" :max-size="100">
        <div class="relative h-full">
          <Map />
        </div>
      </ResizablePanel>
    </ResizablePanelGroup>

    <!-- Main Layout: Карта слева -->
    <ResizablePanelGroup
      v-else-if="layout.mapPosition === 'left'"
      direction="horizontal"
      class="flex-1 h-full"
    >
      <ResizablePanel :default-size="layout.mapSize" :min-size="0" :max-size="100">
        <div class="relative h-full">
          <Map />
        </div>
      </ResizablePanel>
      
      <ResizableHandle withHandle />
      
      <ResizablePanel :default-size="100 - layout.mapSize" :min-size="0" :max-size="100">
        <ResizablePanelGroup direction="vertical">
          <ResizablePanel :default-size="layout.toolsSize" :min-size="0" :max-size="100">
            <div class="relative h-full">
              <BrushTable />
            </div>
          </ResizablePanel>
          
          <ResizableHandle withHandle />
          
          <ResizablePanel :default-size="100 - layout.toolsSize" :min-size="0" :max-size="100">
            <div class="relative h-full">
              <List />
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </ResizablePanel>
    </ResizablePanelGroup>

    <!-- Main Layout: Карта справа -->
    <ResizablePanelGroup
      v-else
      direction="horizontal"
      class="flex-1 h-full"
    >
      <ResizablePanel :default-size="100 - layout.mapSize" :min-size="0" :max-size="100">
        <ResizablePanelGroup direction="vertical">
          <ResizablePanel :default-size="layout.toolsSize" :min-size="0" :max-size="100">
            <div class="relative h-full">
              <BrushTable />
            </div>
          </ResizablePanel>
          
          <ResizableHandle withHandle />
          
          <ResizablePanel :default-size="100 - layout.toolsSize" :min-size="0" :max-size="100">
            <div class="relative h-full">
              <List />
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </ResizablePanel>
      
      <ResizableHandle withHandle />
      
      <ResizablePanel :default-size="layout.mapSize" :min-size="0" :max-size="100">
        <div class="relative h-full">
          <Map />
        </div>
      </ResizablePanel>
    </ResizablePanelGroup>
  </div>
</template>

<style scoped>
/* Адаптивные размеры для панелей */
.resizable-panel {
  min-height: 100px;
  min-width: 100px;
}
</style>
