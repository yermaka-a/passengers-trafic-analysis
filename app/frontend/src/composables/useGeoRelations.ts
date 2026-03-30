/**
 * Composable для работы с гео-связями и авто-назначением маркеров
 */

import { useMapObjectStore } from "@/store";
import { findStopsInPolygon, findStopsNearPolyline } from "@/utils/geoRelations";

export function useGeoRelations() {
  const mapObjectStore = useMapObjectStore();

  /**
   * Автоматически назначить остановки полигонам/полилиниям
   * 
   * @param toleranceMeters Допуск для полилиний (по умолчанию 50м)
   * @returns Количество назначенных связей
   */
  const autoAssignMarkers = async (toleranceMeters: number = 50): Promise<number> => {
    try {
      const allObjects = Array.from(mapObjectStore.Objects.entries());
      
      const polygons = allObjects.filter(([_, obj]) => obj.type === "Polygon");
      const polylines = allObjects.filter(([_, obj]) => obj.type === "Polyline");
      const stops = allObjects
        .filter(([_, obj]) => obj.type === "StopMarker")
        .map(([id, obj]) => ({
          id,
          lat: obj.coordinates?.[0]?.[1] ?? 0,
          lng: obj.coordinates?.[0]?.[0] ?? 0
        }));
      
      let assignedCount = 0;
      const { add_object_relation } = (window as any).pywebview?.api || {};
      
      if (!add_object_relation) {
        console.error("[useGeoRelations] API недоступно");
        return 0;
      }
      
      // Для каждого полигона находим остановки внутри
      for (const [polygonId, polygon] of polygons) {
        const polygonCoords: Array<{lat: number, lng: number}> = polygon.coordinates.map((coord: [number, number]) => ({
          lat: coord[1],
          lng: coord[0]
        }));
        const stopsInPolygon = findStopsInPolygon(stops, polygonCoords);
        
        for (const stop of stopsInPolygon) {
          const result = await add_object_relation({
            parent_id: polygonId,
            child_id: stop.id,
            relation_type: "CONTAINS"
          });
          
          if (result?.status === "success") {
            assignedCount++;
          }
        }
      }
      
      // Для каждой полилинии находим остановки рядом
      for (const [polylineId, polyline] of polylines) {
        const polylineCoords: Array<{lat: number, lng: number}> = polyline.coordinates.map((coord: [number, number]) => ({
          lat: coord[1],
          lng: coord[0]
        }));
        const stopsNearLine = findStopsNearPolyline(stops, polylineCoords, toleranceMeters);
        
        for (const stop of stopsNearLine) {
          const result = await add_object_relation({
            parent_id: polylineId,
            child_id: stop.id,
            relation_type: "NEAR"
          });
          
          if (result?.status === "success") {
            assignedCount++;
          }
        }
      }
      
      console.log(`[useGeoRelations] Назначено связей: ${assignedCount}`);
      return assignedCount;
      
    } catch (e) {
      console.error("[useGeoRelations] autoAssignMarkers error:", e);
      return 0;
    }
  };

  /**
   * Получить все остановки для полигона/полилинии
   * 
   * @param objectId ID полигона/полилинии
   * @returns Список остановок
   */
  const getPolygonStops = async (objectId: string): Promise<any[]> => {
    try {
      const { get_polygon_stops } = (window as any).pywebview?.api || {};
      
      if (!get_polygon_stops) {
        console.error("[useGeoRelations] API недоступно");
        return [];
      }
      
      const result = await get_polygon_stops({ polygon_id: objectId });
      
      if (result?.status === "success") {
        return result.stops || [];
      }
      
      return [];
    } catch (e) {
      console.error("[useGeoRelations] getPolygonStops error:", e);
      return [];
    }
  };

  /**
   * Удалить все связи для объекта
   * 
   * @param objectId ID объекта
   */
  const removeAllRelations = async (objectId: string): Promise<void> => {
    try {
      // Получаем все связи и удаляем
      const stops = await getPolygonStops(objectId);
      const { remove_object_relation } = (window as any).pywebview?.api || {};
      
      if (!remove_object_relation) {
        console.error("[useGeoRelations] API недоступно");
        return;
      }
      
      for (const stop of stops) {
        await remove_object_relation({
          parent_id: objectId,
          child_id: stop.id
        });
      }
    } catch (e) {
      console.error("[useGeoRelations] removeAllRelations error:", e);
    }
  };

  return {
    autoAssignMarkers,
    getPolygonStops,
    removeAllRelations
  };
}
