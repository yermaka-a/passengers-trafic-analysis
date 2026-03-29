/**
 * Иконки для маркеров остановок
 * Lucide SVG paths: https://lucide.dev/icons/
 * 
 * Все иконки используют stroke для изменения цвета через mask в Deck.gl IconLayer
 */

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

// SVG paths из Lucide Icons
const LUCIDE_PATHS = {
  // Bus: https://lucide.dev/icons/bus
  bus: "M8 16h8m-8 4h8m-9-12h10a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2zm2-4h8a2 2 0 0 1 2 2v2H6V6a2 2 0 0 1 2-2z",
  
  // Train Front: https://lucide.dev/icons/train-front
  train: "M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm2 4h12V6H6v2zm0 4h12v-2H6v2zm0 4h12v-2H6v2zm-2 4h2v2H4v-2zm14 0h2v2h-2v-2z",
  
  // Bus Front (для трамвая): https://lucide.dev/icons/bus-front
  tram: "M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm2 4h12V6H6v2zm0 4h12v-2H6v2zm0 4h12v-2H6v2z",
  
  // Car Taxi Front: https://lucide.dev/icons/car-taxi-front
  taxi: "M4 10h16a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2zm2-4h12a2 2 0 0 1 2 2v2H4V8a2 2 0 0 1 2-2zm2 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm12 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4z",
  
  // Car Front: https://lucide.dev/icons/car-front
  car: "M4 10h16a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2zm2-4h12a2 2 0 0 1 2 2v2H4V8a2 2 0 0 1 2-2zm2 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm12 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4z",
  
  // Bike: https://lucide.dev/icons/bike
  bike: "M5 18a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm14 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM5 12h2l2-6h6l2 6h2M12 6v6",
  
  // Map Pin: https://lucide.dev/icons/map-pin
  default: "M12 2c-4.4 0-8 3.6-8 8 0 4.4 8 12 8 12s8-7.6 8-12c0-4.4-3.6-8-8-8zm0 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6z",
};

export const STOP_MARKER_ICONS: Record<StopMarkerType, StopMarkerIcon> = {
  bus: {
    id: 'bus',
    name: 'Bus',
    nameRu: 'Автобус',
    path: LUCIDE_PATHS.bus,
    size: [24, 24],
    anchor: [12, 24],
  },
  train: {
    id: 'train',
    name: 'Train',
    nameRu: 'Поезд',
    path: LUCIDE_PATHS.train,
    size: [24, 24],
    anchor: [12, 24],
  },
  tram: {
    id: 'tram',
    name: 'Tram',
    nameRu: 'Трамвай',
    path: LUCIDE_PATHS.tram,
    size: [24, 24],
    anchor: [12, 24],
  },
  taxi: {
    id: 'taxi',
    name: 'Taxi',
    nameRu: 'Такси',
    path: LUCIDE_PATHS.taxi,
    size: [24, 24],
    anchor: [12, 24],
  },
  car: {
    id: 'car',
    name: 'Car',
    nameRu: 'Легковое авто',
    path: LUCIDE_PATHS.car,
    size: [24, 24],
    anchor: [12, 24],
  },
  bike: {
    id: 'bike',
    name: 'Bike',
    nameRu: 'Велосипед',
    path: LUCIDE_PATHS.bike,
    size: [24, 24],
    anchor: [12, 24],
  },
  default: {
    id: 'default',
    name: 'Default',
    nameRu: 'Стандартный',
    path: LUCIDE_PATHS.default,
    size: [24, 24],
    anchor: [12, 24],
  },
};

console.log('[stopMarkers] STOP_MARKER_ICONS loaded:', Object.keys(STOP_MARKER_ICONS));

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
  
  console.log('[stopMarkers] IconAtlas сгенерирован:', {
    width: atlasWidth,
    height: atlasHeight,
    иконок: icons.length,
  });
  
  return {
    atlas: `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgContent)))}`,
    mapping,
  };
}

export default STOP_MARKER_ICONS;
