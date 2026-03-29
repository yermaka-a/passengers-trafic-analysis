/**
 * Иконки для маркеров остановок на основе Lucide Icons
 * https://lucide.dev/icons/
 * 
 * Все иконки используют fill="currentColor" для изменения цвета через style.color
 */

export type StopMarkerType = 'bus' | 'train' | 'tram' | 'taxi' | 'car' | 'bike' | 'default';

export interface StopMarkerIcon {
  id: StopMarkerType;
  name: string;
  nameRu: string;
  // SVG path data (без SVG обёртки, только path данные)
  path: string;
  // Размер иконки [width, height]
  size: [number, number];
  // Anchor point [x, y] - точка привязки (обычно центр снизу)
  anchor: [number, number];
}

// Иконка автобуса (Lucide: Bus)
const busPath = "M4 8h16a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2zm0-4h16a2 2 0 0 1 2 2v2H2V6a2 2 0 0 1 2-2zm2 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm12 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4z";

// Иконка поезда (Lucide: Train)
const trainPath = "M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm2 4h12V6H6v2zm0 4h12v-2H6v2zm0 4h12v-2H6v2zm-2 4h2v2H4v-2zm14 0h2v2h-2v-2z";

// Иконка трамвая (адаптировано из Lucide: Train Front)
const tramPath = "M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm2 4h12V6H6v2zm0 4h12v-2H6v2zm0 4h12v-2H6v2z";

// Иконка такси (Lucide: Car)
const taxiPath = "M4 10h16a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2zm2-4h12a2 2 0 0 1 2 2v2H4V8a2 2 0 0 1 2-2zm2 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm12 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4z";

// Иконка автомобиля (Lucide: Car)
const carPath = "M4 10h16a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2zm2-4h12a2 2 0 0 1 2 2v2H4V8a2 2 0 0 1 2-2zm2 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm12 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4z";

// Иконка велосипеда (Lucide: Bike)
const bikePath = "M5 18a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm14 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM5 12h2l2-6h6l2 6h2M12 6v6";

// Иконка по умолчанию (Lucide: MapPin)
const defaultPath = "M12 2c-4.4 0-8 3.6-8 8 0 4.4 8 12 8 12s8-7.6 8-12c0-4.4-3.6-8-8-8zm0 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6z";

export const STOP_MARKER_ICONS: Record<StopMarkerType, StopMarkerIcon> = {
  bus: {
    id: 'bus',
    name: 'Bus',
    nameRu: 'Автобус',
    path: busPath,
    size: [24, 24],
    anchor: [12, 24],
  },
  train: {
    id: 'train',
    name: 'Train',
    nameRu: 'Поезд',
    path: trainPath,
    size: [24, 24],
    anchor: [12, 24],
  },
  tram: {
    id: 'tram',
    name: 'Tram',
    nameRu: 'Трамвай',
    path: tramPath,
    size: [24, 24],
    anchor: [12, 24],
  },
  taxi: {
    id: 'taxi',
    name: 'Taxi',
    nameRu: 'Такси',
    path: taxiPath,
    size: [24, 24],
    anchor: [12, 24],
  },
  car: {
    id: 'car',
    name: 'Car',
    nameRu: 'Автомобиль',
    path: carPath,
    size: [24, 24],
    anchor: [12, 24],
  },
  bike: {
    id: 'bike',
    name: 'Bike',
    nameRu: 'Велосипед',
    path: bikePath,
    size: [24, 24],
    anchor: [12, 24],
  },
  default: {
    id: 'default',
    name: 'Default',
    nameRu: 'Маркер',
    path: defaultPath,
    size: [24, 24],
    anchor: [12, 24],
  },
};

/**
 * Получить SVG строку для иконки с указанным цветом
 * @param icon - иконка
 * @param color - цвет в формате [r, g, b, a] (0-255)
 * @returns SVG строка
 */
export function getIconSvg(icon: StopMarkerIcon, color: [number, number, number, number]): string {
  const colorStr = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${colorStr}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${icon.path}"/></svg>`;
}

/**
 * Получить base64 SVG для использования в iconAtlas
 * @param icon - иконка
 * @param color - цвет в формате [r, g, b, a] (0-255)
 * @returns base64 encoded SVG
 */
export function getIconBase64(icon: StopMarkerIcon, color: [number, number, number, number] = [0, 0, 0, 255]): string {
  const svg = getIconSvg(icon, color);
  return `data:image/svg+xml;base64,${btoa(svg)}`;
}

/**
 * Получить данные иконки для Deck.gl IconLayer
 * @param icon - иконка
 * @param color - цвет в формате [r, g, b, a] (0-255)
 * @returns объект для IconLayer
 */
export function getIconData(icon: StopMarkerIcon, color: [number, number, number, number]) {
  return {
    id: icon.id,
    name: icon.name,
    nameRu: icon.nameRu,
    width: icon.size[0],
    height: icon.size[1],
    anchorX: icon.anchor[0],
    anchorY: icon.anchor[1],
    // Масштабирование иконки (можно настроить)
    sx: 1,
    sy: 1,
    // SVG маска для цвета
    svg: getIconSvg(icon, color),
  };
}

export default STOP_MARKER_ICONS;
