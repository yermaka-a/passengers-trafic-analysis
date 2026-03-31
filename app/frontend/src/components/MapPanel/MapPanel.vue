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

const openPassengerFlows = () => {
  // Открываем страницу пассажиропотоков через роутер
  if ((window as any).__VUE_ROUTER__) {
    (window as any).__VUE_ROUTER__.push('/passenger-flows');
  } else {
    // Fallback: открываем в новом окне
    window.open('/passenger-flows', '_blank');
  }
};
</script>

<template>
  <div class="flex flex-col h-screen w-screen">
    <!-- Toolbar с кнопками управления (фиксированный) -->
    <div class="flex justify-between items-center p-2 border-b bg-gray-50 flex-shrink-0">
      <LayoutMenu />
      <div class="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          class="cursor-pointer"
          @click="handleOpenWindow('map')"
          title="Открыть карту в отдельном окне"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1">
            <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/>
            <line x1="9" y1="3" x2="9" y2="18"/>
            <line x1="15" y1="6" x2="15" y2="21"/>
          </svg>
          Карта
        </Button>
        <Button
          variant="outline"
          size="sm"
          class="cursor-pointer"
          @click="handleOpenWindow('list')"
          title="Открыть список в отдельном окне"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1">
            <line x1="8" y1="6" x2="21" y2="6"/>
            <line x1="8" y1="12" x2="21" y2="12"/>
            <line x1="8" y1="18" x2="21" y2="18"/>
            <line x1="3" y1="6" x2="3.01" y2="6"/>
            <line x1="3" y1="12" x2="3.01" y2="12"/>
            <line x1="3" y1="18" x2="3.01" y2="18"/>
          </svg>
          Список
        </Button>
        <Button
          variant="outline"
          size="sm"
          class="cursor-pointer"
          @click="handleOpenWindow('brushTable')"
          title="Открыть инструменты в отдельном окне"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
          Инструменты
        </Button>
        <Button
          variant="outline"
          size="sm"
          class="cursor-pointer"
          @click="openPassengerFlows"
          title="Пассажиропотоки"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1">
            <path d="M3 3v18h18"/>
            <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
          </svg>
          Пассажиропотоки
        </Button>
      </div>
    </div>

    <!-- Main Layout -->
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
