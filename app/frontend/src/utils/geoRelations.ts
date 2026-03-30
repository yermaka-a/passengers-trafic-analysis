/**
 * Гео-вычисления для определения принадлежности маркеров полигонам/полилиниям
 * Использует Turf.js для пространственных операций
 */

import * as turf from "@turf/turf";
import type { Feature, Point, Polygon, LineString, Position } from "geojson";

/**
 * Проверка: принадлежит ли точка полигону
 * 
 * @param lat Широта точки
 * @param lng Долгота точки
 * @param polygonCoords Координаты полигона [{lat, lng}, ...]
 * @returns true если точка внутри полигона
 */
export function isPointInPolygon(
  lat: number,
  lng: number,
  polygonCoords: Array<{ lat: number; lng: number }>
): boolean {
  try {
    const point: Feature<Point> = turf.point([lng, lat]);
    const polygonCoordsFlat: Position[] = polygonCoords.map(c => [c.lng, c.lat]);
    
    // Закрываем полигон (первая точка = последняя)
    const firstCoord = polygonCoordsFlat[0];
    const lastCoord = polygonCoordsFlat[polygonCoordsFlat.length - 1];
    
    if (firstCoord && lastCoord && (firstCoord[0] !== lastCoord[0] || firstCoord[1] !== lastCoord[1])) {
      polygonCoordsFlat.push([...firstCoord]);
    }
    
    const polygon: Feature<Polygon> = turf.polygon([polygonCoordsFlat]);
    return turf.booleanPointInPolygon(point, polygon);
  } catch (e) {
    console.error("isPointInPolygon error:", e);
    return false;
  }
}

/**
 * Проверка: находится ли точка возле линии (с допуском)
 * 
 * @param lat Широта точки
 * @param lng Долгота точки
 * @param lineCoords Координаты линии [{lat, lng}, ...]
 * @param toleranceMeters Допуск в метрах (по умолчанию 50м)
 * @returns true если точка ближе чем toleranceMeters
 */
export function isPointNearLine(
  lat: number,
  lng: number,
  lineCoords: Array<{ lat: number; lng: number }>,
  toleranceMeters: number = 50
): boolean {
  try {
    const point: Feature<Point> = turf.point([lng, lat]);
    const lineCoordsFlat: Position[] = lineCoords.map(c => [c.lng, c.lat]);
    const line: Feature<LineString> = turf.lineString(lineCoordsFlat);
    
    // Находим ближайшую точку на линии
    const nearestPoint = turf.nearestPointOnLine(line, point);
    
    // Вычисляем расстояние в метрах
    const distance = turf.distance(point, nearestPoint, { units: "meters" });
    
    return distance <= toleranceMeters;
  } catch (e) {
    console.error("isPointNearLine error:", e);
    return false;
  }
}

/**
 * Найти все остановки в полигоне
 * 
 * @param stops Список остановок [{id, lat, lng}, ...]
 * @param polygonCoords Координаты полигона [{lat, lng}, ...]
 * @returns Список остановок внутри полигона
 */
export function findStopsInPolygon(
  stops: Array<{ id: string; lat: number; lng: number }>,
  polygonCoords: Array<{ lat: number; lng: number }>
): Array<{ id: string; lat: number; lng: number }> {
  try {
    const polygonCoordsFlat: Position[] = polygonCoords.map(c => [c.lng, c.lat]);
    
    // Закрываем полигон
    const firstCoord = polygonCoordsFlat[0];
    const lastCoord = polygonCoordsFlat[polygonCoordsFlat.length - 1];
    
    if (firstCoord && lastCoord && (firstCoord[0] !== lastCoord[0] || firstCoord[1] !== lastCoord[1])) {
      polygonCoordsFlat.push([...firstCoord]);
    }
    
    const polygon: Feature<Polygon> = turf.polygon([polygonCoordsFlat]);
    
    return stops.filter(stop => {
      const point: Feature<Point> = turf.point([stop.lng, stop.lat]);
      return turf.booleanPointInPolygon(point, polygon);
    });
  } catch (e) {
    console.error("findStopsInPolygon error:", e);
    return [];
  }
}

/**
 * Найти все остановки возле полилинии
 * 
 * @param stops Список остановок [{id, lat, lng}, ...]
 * @param polylineCoords Координаты полилинии [{lat, lng}, ...]
 * @param toleranceMeters Допуск в метрах
 * @returns Список остановок возле полилинии
 */
export function findStopsNearPolyline(
  stops: Array<{ id: string; lat: number; lng: number }>,
  polylineCoords: Array<{ lat: number; lng: number }>,
  toleranceMeters: number = 50
): Array<{ id: string; lat: number; lng: number }> {
  try {
    const lineCoordsFlat: Position[] = polylineCoords.map(c => [c.lng, c.lat]);
    const line: Feature<LineString> = turf.lineString(lineCoordsFlat);
    
    return stops.filter(stop => {
      const point: Feature<Point> = turf.point([stop.lng, stop.lat]);
      const nearestPoint = turf.nearestPointOnLine(line, point);
      const distance = turf.distance(point, nearestPoint, { units: "meters" });
      return distance <= toleranceMeters;
    });
  } catch (e) {
    console.error("findStopsNearPolyline error:", e);
    return [];
  }
}

/**
 * Вычислить расстояние между двумя точками (в метрах)
 * 
 * @param lat1 Широта первой точки
 * @param lng1 Долгота первой точки
 * @param lat2 Широта второй точки
 * @param lng2 Долгота второй точки
 * @returns Расстояние в метрах
 */
export function getDistanceInMeters(
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number
): number {
  try {
    const point1: Feature<Point> = turf.point([lng1, lat1]);
    const point2: Feature<Point> = turf.point([lng2, lat2]);
    return turf.distance(point1, point2, { units: "meters" });
  } catch (e) {
    console.error("getDistanceInMeters error:", e);
    return 0;
  }
}

/**
 * Найти ближайшую остановку к точке
 * 
 * @param lat Широта точки
 * @param lng Долгота точки
 * @param stops Список остановок [{id, lat, lng}, ...]
 * @returns Ближайшая остановка + расстояние в метрах
 */
export function getNearestStop(
  lat: number,
  lng: number,
  stops: Array<{ id: string; lat: number; lng: number }>
): { id: string; lat: number; lng: number; distanceMeters: number } | null {
  if (stops.length === 0) return null;
  
  let nearestStop = null;
  let minDistance = Infinity;
  
  for (const stop of stops) {
    const distance = getDistanceInMeters(lat, lng, stop.lat, stop.lng);
    if (distance < minDistance) {
      minDistance = distance;
      nearestStop = stop;
    }
  }
  
  return nearestStop ? { ...nearestStop, distanceMeters: minDistance } : null;
}

/**
 * Вычислить длину линии (в метрах)
 * 
 * @param lineCoords Координаты линии [{lat, lng}, ...]
 * @returns Длина в метрах
 */
export function getLineLength(lineCoords: Array<{ lat: number; lng: number }>): number {
  try {
    const lineCoordsFlat: Position[] = lineCoords.map(c => [c.lng, c.lat]);
    const line: Feature<LineString> = turf.lineString(lineCoordsFlat);
    return turf.length(line, { units: "meters" });
  } catch (e) {
    console.error("getLineLength error:", e);
    return 0;
  }
}

/**
 * Вычислить площадь полигона (в квадратных метрах)
 * 
 * @param polygonCoords Координаты полигона [{lat, lng}, ...]
 * @returns Площадь в квадратных метрах
 */
export function getPolygonArea(polygonCoords: Array<{ lat: number; lng: number }>): number {
  try {
    const polygonCoordsFlat: Position[] = polygonCoords.map(c => [c.lng, c.lat]);
    
    // Закрываем полигон
    const firstCoord = polygonCoordsFlat[0];
    const lastCoord = polygonCoordsFlat[polygonCoordsFlat.length - 1];
    
    if (firstCoord && lastCoord && (firstCoord[0] !== lastCoord[0] || firstCoord[1] !== lastCoord[1])) {
      polygonCoordsFlat.push([...firstCoord]);
    }
    
    const polygon: Feature<Polygon> = turf.polygon([polygonCoordsFlat]);
    return turf.area(polygon); // Возвращает площадь в квадратных метрах
  } catch (e) {
    console.error("getPolygonArea error:", e);
    return 0;
  }
}
