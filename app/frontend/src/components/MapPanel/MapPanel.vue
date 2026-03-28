<script lang="ts" setup>
import { Map } from "@/components/Map";
import { List } from "@/components/List";
import BrushTable from "@/components/BrushTable/BrushTable.vue";
import PanelContainer from "@/components/PanelContainer/PanelContainer.vue";
import { Button } from "@/components/ui/button";
import draggable from "vuedraggable";
import { usePanelLayoutStore } from "@/store/usePanelLayoutStore";
import { computed } from "vue";

const layoutStore = usePanelLayoutStore();

// Получаем видимые панели, отсортированные по позиции
const visiblePanels = computed(() => layoutStore.getVisiblePanels());

// Компоненты для динамического рендеринга
const componentMap: Record<string, any> = {
  map: Map,
  list: List,
  brushTable: BrushTable,
};

// Обработчики для кнопок
const handleOpenWindow = (panelId: string) => {
  layoutStore.openPanelInWindow(panelId);
};

const handleCloseWindow = (panelId: string) => {
  layoutStore.closeFloatingPanel(panelId);
};

const handleResetLayout = () => {
  if (confirm("Сбросить layout к значениям по умолчанию?")) {
    layoutStore.resetLayout();
  }
};
</script>

<template>
  <div class="flex flex-col gap-3 p-3">
    <!-- Toolbar с кнопками управления -->
    <div class="flex justify-between items-center bg-gray-50 p-2 rounded-lg border">
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-600">
          🖱️ Перетаскивайте панели за значок ≡
        </span>
      </div>
      <Button
        variant="outline"
        size="sm"
        @click="handleResetLayout"
        class="text-xs"
      >
        🔄 Сбросить layout
      </Button>
    </div>

    <!-- Draggable область для панелей -->
    <draggable
      v-model="layoutStore.panels"
      item-key="id"
      animation="300"
      ghost-class="dragging-ghost"
      chosen-class="dragging-chosen"
      drag-class="dragging"
      class="flex flex-col gap-3"
    >
      <template #item="{ element }">
        <div v-if="element.isVisible && !element.isFloating">
          <PanelContainer
            :panel="element"
            @open-window="handleOpenWindow"
            @close-window="handleCloseWindow"
          >
            <component :is="componentMap[element.id]" />
          </PanelContainer>
        </div>
      </template>
    </draggable>
  </div>
</template>

<style scoped>
/* Стили для drag-and-drop */
.dragging-ghost {
  opacity: 0.5;
  background: #f3f4f6;
  border: 2px dashed #9ca3af;
}

.dragging-chosen {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  transform: scale(1.02);
}

.dragging {
  cursor: grabbing;
}

/* Анимация перемещения */
.flip-list-move {
  transition: transform 0.3s ease-out;
}
</style>
