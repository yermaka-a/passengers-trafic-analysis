/**
 * Иконки для гео-маркеров (pin, flag, balloon)
 * Lucide SVG paths: https://lucide.dev/icons/
 *
 * Все иконки используют stroke для изменения цвета через mask в Deck.gl IconLayer
 */

export type StopMarkerType = 'pin' | 'pinned' | 'flag' | 'flag-check' | 'pin-check' | 'pin-plus' | 'balloon';

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
  // MapPin: https://lucide.dev/icons/map-pin
  pin: "M20 10c0 4.993-8 13-8 13s-8-8.007-8-13a8 8 0 1 1 16 0Z",

  // MapPinned: https://lucide.dev/icons/map-pinned
  pinned: "M12 2C8.13 2 5 5.13 5 12c0 5.25 7 13 7 13s7-7.75 7-13c0-6.87-3.13-10-7-10zm0 18c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z",

  // Flag: https://lucide.dev/icons/flag
  flag: "M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1zM4 22v-7",

  // FlagCheck: https://lucide.dev/icons/flag-check
  'flag-check': "M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1zM4 22v-7m-2 4 4 4 6-6",

  // MapPinCheck: https://lucide.dev/icons/map-pin-check
  'pin-check': "M20 10c0 4.993-8 13-8 13s-8-8.007-8-13a8 8 0 1 1 16 0Zm-2 2-4 4-2-2",

  // MapPinPlus: https://lucide.dev/icons/map-pin-plus
  'pin-plus': "M20 10c0 4.993-8 13-8 13s-8-8.007-8-13a8 8 0 1 1 16 0Zm-2 2h-2m-1-1v-2m0 6v-2",

  // Balloon: https://lucide.dev/icons/balloon
  balloon: "M6 9a8 8 0 1 1 12 0c0 4.993-6 13-6 13S6 13.993 6 9zm6 13v-4",
};

export const STOP_MARKER_ICONS: Record<StopMarkerType, StopMarkerIcon> = {
  pin: {
    id: 'pin',
    name: 'MapPin',
    nameRu: 'Маркер',
    path: LUCIDE_PATHS.pin,
    size: [24, 24],
    anchor: [12, 24],
  },
  pinned: {
    id: 'pinned',
    name: 'MapPinned',
    nameRu: 'Закреплён',
    path: LUCIDE_PATHS.pinned,
    size: [24, 24],
    anchor: [12, 24],
  },
  flag: {
    id: 'flag',
    name: 'Flag',
    nameRu: 'Флаг',
    path: LUCIDE_PATHS.flag,
    size: [24, 24],
    anchor: [12, 24],
  },
  'flag-check': {
    id: 'flag-check',
    name: 'FlagCheck',
    nameRu: 'Флаг (отмечен)',
    path: LUCIDE_PATHS['flag-check'],
    size: [24, 24],
    anchor: [12, 24],
  },
  'pin-check': {
    id: 'pin-check',
    name: 'MapPinCheck',
    nameRu: 'Маркер (отмечен)',
    path: LUCIDE_PATHS['pin-check'],
    size: [24, 24],
    anchor: [12, 24],
  },
  'pin-plus': {
    id: 'pin-plus',
    name: 'MapPinPlus',
    nameRu: 'Маркер (+)',
    path: LUCIDE_PATHS['pin-plus'],
    size: [24, 24],
    anchor: [12, 24],
  },
  balloon: {
    id: 'balloon',
    name: 'Balloon',
    nameRu: 'Шарик',
    path: LUCIDE_PATHS.balloon,
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
