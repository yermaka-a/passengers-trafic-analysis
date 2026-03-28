import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface PanelConfig {
  id: 'map' | 'list' | 'brushTable';
  title: string;
  isFloating: boolean;
  windowRef: Window | null;
  isVisible: boolean;
}

const STORAGE_KEY = 'panelFloatingState';

export const usePanelLayoutStore = defineStore('panelLayout', () => {
  const panels = ref<PanelConfig[]>([
    {
      id: 'brushTable',
      title: '🎨 Инструменты',
      isFloating: false,
      windowRef: null,
      isVisible: true,
    },
    {
      id: 'list',
      title: '📋 Список объектов',
      isFloating: false,
      windowRef: null,
      isVisible: true,
    },
    {
      id: 'map',
      title: '🗺️ Карта',
      isFloating: false,
      windowRef: null,
      isVisible: true,
    },
  ]);

  // BroadcastChannel для синхронизации между окнами
  const channel = new BroadcastChannel('panel-sync');

  // Инициализация - загрузка из localStorage
  const initLayout = () => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const savedState = JSON.parse(saved);
        panels.value.forEach(panel => {
          const savedPanel = savedState.find((p: any) => p.id === panel.id);
          if (savedPanel) {
            panel.isFloating = savedPanel.isFloating || false;
          }
        });
      } catch (e) {
        console.error('[PanelLayout] Error loading saved state:', e);
      }
    }
  };

  // Сохранение в localStorage
  const saveState = () => {
    const state = panels.value.map(p => ({
      id: p.id,
      isFloating: p.isFloating,
    }));
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  };

  // Открытие панели в отдельном окне
  const openPanelInWindow = (panelId: string) => {
    const panel = panels.value.find(p => p.id === panelId);
    if (!panel || panel.isFloating) return;

    const url = `${window.location.origin}?panel=${panelId}`;
    const features = 'width=1000,height=700,menubar=no,toolbar=no';
    const newWindow = window.open(url, `panel-${panelId}`, features);

    if (newWindow) {
      panel.isFloating = true;
      panel.windowRef = newWindow;
      panel.isVisible = false;

      // Слушаем закрытие окна
      const checkClosed = setInterval(() => {
        if (newWindow.closed) {
          panel.isFloating = false;
          panel.windowRef = null;
          panel.isVisible = true;
          clearInterval(checkClosed);
          saveState();
          
          channel.postMessage({
            type: 'PANEL_CLOSED',
            panelId,
          });
        }
      }, 500);
      
      saveState();
    }
  };

  // Закрытие плавающей панели
  const closeFloatingPanel = (panelId: string) => {
    const panel = panels.value.find(p => p.id === panelId);
    if (panel?.windowRef) {
      panel.windowRef.close();
    }
  };

  // Показать только одну панель (для режима отдельного окна)
  const showOnlyPanel = (panelId: string) => {
    panels.value.forEach(panel => {
      panel.isVisible = panel.id === panelId;
    });
  };

  // Получить панель по ID
  const getPanel = (panelId: string) => {
    return panels.value.find(p => p.id === panelId);
  };

  // Обработка сообщений от других окон
  channel.onmessage = (event) => {
    const { type, panelId } = event.data;
    
    if (type === 'PANEL_CLOSED') {
      const panel = panels.value.find(p => p.id === panelId);
      if (panel) {
        panel.isFloating = false;
        panel.windowRef = null;
        panel.isVisible = true;
      }
    }
  };

  return {
    panels,
    initLayout,
    openPanelInWindow,
    closeFloatingPanel,
    showOnlyPanel,
    getPanel,
  };
});
