import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import type { Component } from 'vue';
import { Map } from '@/components/Map';
import { List } from '@/components/List';
import BrushTable from '@/components/BrushTable/BrushTable.vue';

export interface PanelConfig {
  id: 'map' | 'list' | 'brushTable';
  title: string;
  component: Component;
  position: number;
  isFloating: boolean;
  windowRef: Window | null;
  isVisible: boolean;
}

export interface PanelLayoutState {
  panels: PanelConfig[];
  layoutOrder: string[];
}

const STORAGE_KEY = 'panelLayout';

export const usePanelLayoutStore = defineStore('panelLayout', () => {
  const panels = ref<PanelConfig[]>([
    {
      id: 'brushTable',
      title: '🎨 Инструменты',
      component: BrushTable,
      position: 0,
      isFloating: false,
      windowRef: null,
      isVisible: true,
    },
    {
      id: 'list',
      title: '📋 Список объектов',
      component: List,
      position: 1,
      isFloating: false,
      windowRef: null,
      isVisible: true,
    },
    {
      id: 'map',
      title: '🗺️ Карта',
      component: Map,
      position: 2,
      isFloating: false,
      windowRef: null,
      isVisible: true,
    },
  ]);

  const layoutOrder = ref<string[]>(['brushTable', 'list', 'map']);

  // BroadcastChannel для синхронизации между окнами
  const channel = new BroadcastChannel('panel-sync');

  // Инициализация - загрузка из localStorage
  const initLayout = () => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const savedOrder = JSON.parse(saved);
        if (Array.isArray(savedOrder) && savedOrder.length === 3) {
          layoutOrder.value = savedOrder;
          
          // Обновляем позиции панелей
          panels.value.forEach(panel => {
            panel.position = layoutOrder.value.indexOf(panel.id);
          });
        }
      } catch (e) {
        console.error('[PanelLayout] Error loading saved layout:', e);
      }
    }
  };

  // Сохранение в localStorage
  const saveLayout = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(layoutOrder.value));
  };

  // Обновление порядка панелей
  const updateLayoutOrder = (newOrder: string[]) => {
    layoutOrder.value = newOrder;
    panels.value.forEach(panel => {
      panel.position = newOrder.indexOf(panel.id);
    });
    saveLayout();
    
    // Отправляем уведомление другим окнам
    channel.postMessage({
      type: 'LAYOUT_UPDATED',
      order: newOrder,
    });
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
          
          channel.postMessage({
            type: 'PANEL_CLOSED',
            panelId,
          });
        }
      }, 500);
    }
  };

  // Закрытие плавающей панели
  const closeFloatingPanel = (panelId: string) => {
    const panel = panels.value.find(p => p.id === panelId);
    if (panel?.windowRef) {
      panel.windowRef.close();
      panel.isFloating = false;
      panel.windowRef = null;
      panel.isVisible = true;
    }
  };

  // Показать только одну панель (для режима отдельного окна)
  const showOnlyPanel = (panelId: string) => {
    panels.value.forEach(panel => {
      panel.isVisible = panel.id === panelId;
    });
  };

  // Сброс layout к значениям по умолчанию
  const resetLayout = () => {
    layoutOrder.value = ['brushTable', 'list', 'map'];
    panels.value.forEach(panel => {
      panel.position = layoutOrder.value.indexOf(panel.id);
      if (panel.isFloating) {
        closeFloatingPanel(panel.id);
      }
    });
    saveLayout();
  };

  // Получить панель по ID
  const getPanel = (panelId: string) => {
    return panels.value.find(p => p.id === panelId);
  };

  // Получить видимые панели (для основного окна)
  const getVisiblePanels = () => {
    return panels.value
      .filter(p => p.isVisible && !p.isFloating)
      .sort((a, b) => a.position - b.position);
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

  // Сохранение при изменении порядка
  watch(layoutOrder, saveLayout);

  return {
    panels,
    layoutOrder,
    initLayout,
    updateLayoutOrder,
    openPanelInWindow,
    closeFloatingPanel,
    showOnlyPanel,
    resetLayout,
    getPanel,
    getVisiblePanels,
  };
});
