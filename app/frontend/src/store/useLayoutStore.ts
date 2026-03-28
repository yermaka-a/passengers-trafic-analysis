import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

export type MapPosition = 'top' | 'bottom' | 'left' | 'right';

export interface LayoutConfig {
  mapPosition: MapPosition;  // Позиция карты
  mapSize: number;           // Размер карты (0-100)
  toolsSize: number;         // Размер BrushTable (0-100)
}

const STORAGE_KEY = 'panelLayout';

const defaultLayout: LayoutConfig = {
  mapPosition: 'right',
  mapSize: 60,
  toolsSize: 25,
};

export const useLayoutStore = defineStore('layout', () => {
  const layout = ref<LayoutConfig>({ ...defaultLayout });

  // Загрузка из localStorage
  const loadFromStorage = () => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        layout.value = { ...defaultLayout, ...parsed };
        console.log('[LayoutStore] Loaded from storage:', layout.value);
      } catch (e) {
        console.error('[LayoutStore] Error loading from storage:', e);
      }
    }
  };

  // Сохранение в localStorage
  const saveToStorage = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(layout.value));
  };

  // Установка позиции карты
  const setMapPosition = (position: MapPosition) => {
    layout.value.mapPosition = position;
    saveToStorage();
    console.log('[LayoutStore] Set map position:', position);
  };

  // Установка размера карты
  const setMapSize = (size: number) => {
    layout.value.mapSize = size;
    saveToStorage();
  };

  // Установка размера инструментов
  const setToolsSize = (size: number) => {
    layout.value.toolsSize = size;
    saveToStorage();
  };

  // Сброс к значениям по умолчанию
  const resetLayout = () => {
    layout.value = { ...defaultLayout };
    saveToStorage();
  };

  // Инициализация
  loadFromStorage();

  // Сохранение при изменении
  watch(layout, saveToStorage, { deep: true });

  return {
    layout,
    setMapPosition,
    setMapSize,
    setToolsSize,
    resetLayout,
  };
});
