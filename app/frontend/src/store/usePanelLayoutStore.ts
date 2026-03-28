import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface PanelConfig {
  id: 'map' | 'list' | 'brushTable';
  title: string;
  isFloating: boolean;
  isVisible: boolean;
}

export const usePanelLayoutStore = defineStore('panelLayout', () => {
  const panels = ref<PanelConfig[]>([
    {
      id: 'brushTable',
      title: '🎨 Инструменты',
      isFloating: false,
      isVisible: true,
    },
    {
      id: 'list',
      title: '📋 Список объектов',
      isFloating: false,
      isVisible: true,
    },
    {
      id: 'map',
      title: '🗺️ Карта',
      isFloating: false,
      isVisible: true,
    },
  ]);

  // BroadcastChannel для синхронизации между окнами
  const channel = new BroadcastChannel('panel-sync');

  // Показать только одну панель (для режима отдельного окна)
  const showOnlyPanel = (panelId: string) => {
    panels.value.forEach(panel => {
      panel.isVisible = panel.id === panelId;
    });
  };

  // Обработка сообщений от других окон
  channel.onmessage = (event) => {
    console.log('[PanelLayout] Message received:', event.data);
  };

  return {
    panels,
    showOnlyPanel,
  };
});
