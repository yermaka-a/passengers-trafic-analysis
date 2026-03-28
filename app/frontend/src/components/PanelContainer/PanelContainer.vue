<script setup lang="ts">
import { Button } from '@/components/ui/button';
import type { PanelConfig } from '@/store/usePanelLayoutStore';

interface Props {
  panel: PanelConfig;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  openWindow: [panelId: string];
  closeWindow: [panelId: string];
}>();
</script>

<template>
  <div class="panel-container border rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow">
    <!-- Header панели -->
    <div class="panel-header flex justify-between items-center p-3 bg-gradient-to-r from-gray-50 to-gray-100 border-b rounded-t-lg">
      <!-- Drag handle (визуальный индикатор) -->
      <div class="flex items-center gap-2">
        <span class="drag-handle cursor-move text-gray-400 hover:text-gray-600 p-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="8" y1="6" x2="21" y2="6"></line>
            <line x1="8" y1="12" x2="21" y2="12"></line>
            <line x1="8" y1="18" x2="21" y2="18"></line>
            <line x1="3" y1="6" x2="3.01" y2="6"></line>
            <line x1="3" y1="12" x2="3.01" y2="12"></line>
            <line x1="3" y1="18" x2="3.01" y2="18"></line>
          </svg>
        </span>
        <span class="font-semibold text-sm text-gray-700">{{ panel.title }}</span>
      </div>
      
      <!-- Кнопки управления -->
      <div class="flex gap-1">
        <Button
          v-if="!panel.isFloating"
          variant="outline"
          size="sm"
          class="h-7 px-2 text-xs"
          @click="emit('openWindow', panel.id)"
          title="Открыть в отдельном окне"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
            <polyline points="15 3 21 3 21 9"></polyline>
            <line x1="10" y1="14" x2="21" y2="3"></line>
          </svg>
          Окно
        </Button>
        <Button
          v-else
          variant="destructive"
          size="sm"
          class="h-7 px-2 text-xs"
          @click="emit('closeWindow', panel.id)"
          title="Закрыть окно"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </Button>
      </div>
    </div>
    
    <!-- Контент панели -->
    <div class="panel-content p-3">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.panel-container {
  animation: panelFadeIn 0.3s ease-out;
}

@keyframes panelFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.drag-handle:hover {
  color: var(--primary);
}
</style>
