import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

export type LayoutOrientation = 'horizontal' | 'vertical';
export type MapPosition = 'left' | 'right' | 'top' | 'bottom';

export interface LayoutConfig {
  orientation: LayoutOrientation;  // Главное направление
  leftOrientation: 'vertical' | 'horizontal';  // Для левой панели
  mapPosition: MapPosition;
  brushSize: number;  // Процент
  listSize: number;
  mapSize: number;
}

const STORAGE_KEY = 'panelLayout';

const defaultLayout: LayoutConfig = {
  orientation: 'horizontal',
  leftOrientation: 'vertical',
  mapPosition: 'right',
  brushSize: 25,
  listSize: 75,
  mapSize: 60,
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

  // Обновление layout
  const setLayout = (config: Partial<LayoutConfig>) => {
    layout.value = { ...layout.value, ...config };
    saveToStorage();
  };

  // Позиция карты
  const setMapPosition = (position: MapPosition) => {
    layout.value.mapPosition = position;
    
    // Меняем ориентацию в зависимости от позиции
    if (position === 'top' || position === 'bottom') {
      // Карта сверху/снизу - главная ориентация vertical
      layout.value.orientation = 'vertical';
      layout.value.leftOrientation = 'horizontal';
    } else {
      // Карта слева/справа - главная ориентация horizontal
      layout.value.orientation = 'horizontal';
      layout.value.leftOrientation = 'vertical';
    }
    
    saveToStorage();
    console.log('[LayoutStore] Set map position:', position, layout.value);
  };

  // Переключение ориентации
  const toggleOrientation = () => {
    layout.value.orientation = layout.value.orientation === 'horizontal' ? 'vertical' : 'horizontal';
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
    setLayout,
    setMapPosition,
    toggleOrientation,
    resetLayout,
  };
});
