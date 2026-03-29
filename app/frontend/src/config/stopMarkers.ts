/**
 * Иконки для маркеров остановок из lucide-vue-next
 * 
 * Все иконки используют stroke для изменения цвета через mask в Deck.gl IconLayer
 */

import {
  Bus,
  BusFront,
  TrainFront,
  CarTaxiFront,
  CarFront,
  Bike,
  MapPin,
} from "lucide-vue-next";

export type StopMarkerType = 'bus' | 'train' | 'tram' | 'taxi' | 'car' | 'bike' | 'default';

export interface StopMarkerIcon {
  id: StopMarkerType;
  name: string;
  nameRu: string;
  // SVG path data
  path: string;
  // Размер иконки [width, height]
  size: [number, number];
  // Anchor point [x, y] - точка привязки (обычно центр снизу)
  anchor: [number, number];
}

// Извлекаем path из Lucide компонента
const getPathFromLucideComponent = (component: any): string => {
  if (!component || !component.render) return '';
  
  // Для lucide-vue-next компоненты хранят template с SVG
  const template = component.render.toString();
  const match = template.match(/d="([^"]*)"/g);
  if (!match) return '';
  
  // Берём все path и объединяем
  const paths = match.map((m: string) => {
    const pathMatch = m.match(/d="([^"]*)"/);
    return pathMatch ? pathMatch[1] : '';
  }).filter(Boolean);
  
  return paths.join(' ');
};

export const STOP_MARKER_ICONS: Record<StopMarkerType, StopMarkerIcon> = {
  bus: {
    id: 'bus',
    name: 'Bus',
    nameRu: 'Автобус',
    path: getPathFromLucideComponent(Bus),
    size: [24, 24],
    anchor: [12, 24],
  },
  train: {
    id: 'train',
    name: 'Train',
    nameRu: 'Поезд',
    path: getPathFromLucideComponent(TrainFront),
    size: [24, 24],
    anchor: [12, 24],
  },
  tram: {
    id: 'tram',
    name: 'Tram',
    nameRu: 'Трамвай',
    path: getPathFromLucideComponent(BusFront), // Используем BusFront как заглушку
    size: [24, 24],
    anchor: [12, 24],
  },
  taxi: {
    id: 'taxi',
    name: 'Taxi',
    nameRu: 'Такси',
    path: getPathFromLucideComponent(CarTaxiFront),
    size: [24, 24],
    anchor: [12, 24],
  },
  car: {
    id: 'car',
    name: 'Car',
    nameRu: 'Автомобиль',
    path: getPathFromLucideComponent(CarFront),
    size: [24, 24],
    anchor: [12, 24],
  },
  bike: {
    id: 'bike',
    name: 'Bike',
    nameRu: 'Велосипед',
    path: getPathFromLucideComponent(Bike),
    size: [24, 24],
    anchor: [12, 24],
  },
  default: {
    id: 'default',
    name: 'Default',
    nameRu: 'Маркер',
    path: getPathFromLucideComponent(MapPin),
    size: [24, 24],
    anchor: [12, 24],
  },
};

/**
 * Получить SVG строку для иконки с указанным цветом
 */
export function getIconSvg(icon: StopMarkerIcon, color: [number, number, number, number]): string {
  const colorStr = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${colorStr}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${icon.path}"/></svg>`;
}

/**
 * Получить base64 SVG для использования в iconAtlas
 */
export function getIconBase64(icon: StopMarkerIcon, color: [number, number, number, number] = [0, 0, 0, 255]): string {
  const svg = getIconSvg(icon, color);
  return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`;
}

/**
 * Сгенерировать sprite atlas из всех иконок
 */
export function generateIconAtlas(): {
  atlas: string;
  mapping: Record<string, { x: number; y: number; width: number; height: number; anchorX: number; anchorY: number; mask: boolean }>;
} {
  const iconSize = 24;
  const icons = Object.entries(STOP_MARKER_ICONS);
  const atlasWidth = icons.length * iconSize;
  const atlasHeight = iconSize;
  
  // Генерируем SVG sprite
  let svgContent = `<svg xmlns="http://www.w3.org/2000/svg" width="${atlasWidth}" height="${atlasHeight}" viewBox="0 0 ${atlasWidth} ${atlasHeight}">`;
  
  const mapping: Record<string, any> = {};
  
  icons.forEach(([key, icon], index) => {
    const x = index * iconSize;
    mapping[key] = {
      x,
      y: 0,
      width: iconSize,
      height: iconSize,
      anchorX: iconSize / 2,
      anchorY: iconSize,
      mask: true,
    };
    
    // Добавляем path с правильным offset
    svgContent += `<g transform="translate(${x}, 0)"><path d="${icon.path}" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>`;
  });
  
  svgContent += `</svg>`;
  
  return {
    atlas: `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`,
    mapping,
  };
}

export default STOP_MARKER_ICONS;
