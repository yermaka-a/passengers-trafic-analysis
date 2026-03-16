/**
 * Утилиты для конвертации цветов
 *
 * Бэкенд использует hex формат (#RRGGBB)
 * Deck.gl использует RGBA массив [r, g, b, a] где каждый компонент 0-255
 */

export type RGBAColor = [number, number, number, number];
export type HexColor = string;

/**
 * Конвертирует hex цвет (#RRGGBB) → RGBA массив [0-255]
 * @param hex - hex цвет в формате #RRGGBB
 * @param alpha - прозрачность (0-255), по умолчанию 255
 */
export const hexToRGBA = (hex: string, alpha: number = 255): RGBAColor => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return [0, 0, 0, alpha];

  return [
    parseInt(result[1]!, 16),
    parseInt(result[2]!, 16),
    parseInt(result[3]!, 16),
    alpha,
  ];
};

/**
 * Конвертирует RGBA → hex (#RRGGBB)
 * @param rgba - массив [r, g, b, a]
 */
export const rgbaToHex = ([r, g, b]: RGBAColor): HexColor => {
  console.log(
    "rgbatohex: ",
    `#${[r, g, b].map((c) => Math.round(c).toString(16).padStart(2, "0")).join("")}`,
  );
  return `#${[r, g, b].map((c) => Math.round(c).toString(16).padStart(2, "0")).join("")}`;
};

/**
 * Парсит CSS цвет (named color, rgb, rgba, hsl) → RGBA
 */
export const parseCSSToRGBA = (color: string): RGBAColor => {
  const ctx = document.createElement("canvas").getContext("2d");
  if (!ctx) return [0, 0, 0, 255];

  ctx.fillStyle = color;
  const computed = ctx.fillStyle;

  const match = computed.match(
    /^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)$/,
  );
  if (!match) return [0, 0, 0, 255];

  return [
    parseInt(match[1]!, 10),
    parseInt(match[2]!, 10),
    parseInt(match[3]!, 10),
    Math.round(parseFloat(match[4] ?? "1") * 255),
  ];
};
