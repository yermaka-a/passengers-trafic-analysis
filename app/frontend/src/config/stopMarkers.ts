/**
 * Иконки для маркеров остановок
 * Все иконки используют currentColor для fill, что позволяет менять цвет через style.color
 */

export type StopMarkerType = 'bus' | 'train' | 'tram' | 'trolleybus' | 'metro' | 'default';

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

// Иконка автобуса
const busPath = "M12 2C8 2 4 3 4 6v10c0 1.1 0.9 2 2 2h1v2c0 0.55 0.45 1 1 1h1c0.55 0 1-0.45 1-1v-2h4v2c0 0.55 0.45 1 1 1h1c0.55 0 1-0.45 1-1v-2h1c1.1 0 2-0.9 2-2V6c0-3-4-4-8-4zm0 2c3 0 5 0.5 5 2H7c0-1.5 2-2 5-2zm5 11H7v-1h10v1zm0-3H7V7h10v5z";

// Иконка поезда/электрички
const trainPath = "M12 2c-4 0-8 4-8 9v7l2 2h12l2-2v-7c0-5-4-9-8-9zm0 2c2.5 0 4.5 2 4.5 4H7.5c0-2 2-4 4.5-4zm-5 9v-1h10v1H7zm0-2V7h10v4H7z";

// Иконка трамвая
const tramPath = "M12 2C8 2 4 3 4 6v11c0 1.1 0.9 2 2 2h1v1c0 0.55 0.45 1 1 1h1c0.55 0 1-0.45 1-1v-1h4v1c0 0.55 0.45 1 1 1h1c0.55 0 1-0.45 1-1v-1h1c1.1 0 2-0.9 2-2V6c0-3-4-4-8-4zm0 2c3 0 5 0.5 5 2H7c0-1.5 2-2 5-2zm5 11H7v-1h10v1zm0-3H7V7h10v5z";

// Иконка троллейбуса
const trolleybusPath = "M12 2C8 2 4 3 4 6v10c0 1.1 0.9 2 2 2h1v2c0 0.55 0.45 1 1 1h1c0.55 0 1-0.45 1-1v-2h4v2c0 0.55 0.45 1 1 1h1c0.55 0 1-0.45 1-1v-2h1c1.1 0 2-0.9 2-2V6c0-3-4-4-8-4zm0 2c3 0 5 0.5 5 2H7c0-1.5 2-2 5-2zm5 11H7v-1h10v1zm-1-9l-1 4H9l-1-4h4z";

// Иконка метро (станция)
const metroPath = "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z";

// Иконка по умолчанию (круг с точкой)
const defaultPath = "M12 2C8.13 2 5 5.13 5 12c0 5.25 7 13 7 13s7-7.75 7-13c0-6.87-3.13-10-7-10zm0 13c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z";

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
  trolleybus: {
    id: 'trolleybus',
    name: 'Trolleybus',
    nameRu: 'Троллейбус',
    path: trolleybusPath,
    size: [24, 24],
    anchor: [12, 24],
  },
  metro: {
    id: 'metro',
    name: 'Metro',
    nameRu: 'Метро',
    path: metroPath,
    size: [24, 24],
    anchor: [12, 24],
  },
  default: {
    id: 'default',
    name: 'Default',
    nameRu: 'По умолчанию',
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
  const colorStr = `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${color[3] / 255})`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${icon.size[0]} ${icon.size[1]}" width="${icon.size[0]}" height="${icon.size[1]}"><path fill="${colorStr}" d="${icon.path}"/></svg>`;
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
