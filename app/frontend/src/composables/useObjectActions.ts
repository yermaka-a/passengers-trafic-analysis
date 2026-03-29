import { useMapObjectStore } from "@/store/useMapObjectStore";
import { useMapStore } from "@/store";
import { useApi } from "@/composables";
import type { DeckGLObject } from "@/types";
import { hexToRGBA } from "@/utils";

/**
 * Composable для управления действиями с объектами
 * Используется в ObjectListView и PropertyTable
 */
export const useObjectActions = () => {
  const mapObjectStore = useMapObjectStore();
  const mapStore = useMapStore();
  const { deleteObject, updateObject } = useApi();

  /**
   * Изменить цвет объекта
   */
  const changeColor = async (value: string, id: string) => {
    if (!value) return;
    const newColor = hexToRGBA(value);
    
    mapObjectStore.updateObjectStyle(id, {
      color: newColor,
    });

    const updatedObj = mapObjectStore.getObjectById(id);
    if (updatedObj) {
      await updateObjectInBackend(updatedObj);
    }
  };

  /**
   * Переключить видимость обводки
   */
  const toggleStroke = async (id: string) => {
    const obj = mapObjectStore.Objects.get(id);
    if (obj) {
      const hide = (obj.style.strokeWidth ?? 0) > 0;
      mapObjectStore.toggleStrokeVisibility(id, hide);
      const updatedObj = mapObjectStore.getObjectById(id);
      if (updatedObj) await updateObjectInBackend(updatedObj);
    }
  };

  /**
   * Изменить пунктир
   */
  const changeDash = async (value: number[], id: string) => {
    const obj = mapObjectStore.Objects.get(id);
    // Не применяем пунктир к StopMarker и CircleMarker
    if (obj && value && obj.type !== 'StopMarker' && obj.type !== 'CircleMarker') {
      const dashValue =
        value[0] === 0 ? [0, 0] : ([value[0], value[0]! / 2] as [number, number]);

      mapObjectStore.updateObjectStyle(id, {
        strokeDasharray: dashValue as [number, number],
      });
      const updatedObj = mapObjectStore.getObjectById(id);
      if (updatedObj) await updateObjectInBackend(updatedObj);
    }
  };

  /**
   * Изменить прозрачность заливки
   */
  const changeFillOpacity = async (value: number[], id: string) => {
    const obj = mapObjectStore.Objects.get(id);
    // Не применяем прозрачность к StopMarker
    if (obj && value && obj.type !== 'StopMarker') {
      mapObjectStore.updateObjectStyle(id, { fillOpacity: value[0] });
      const updatedObj = mapObjectStore.getObjectById(id);
      if (updatedObj) await updateObjectInBackend(updatedObj);
    }
  };

  /**
   * Изменить жирность обводки
   */
  const changeWeight = async (value: number[], id: string) => {
    const obj = mapObjectStore.Objects.get(id);
    // Не применяем обводку к StopMarker
    if (obj && value && obj.type !== 'StopMarker') {
      mapObjectStore.updateObjectStyle(id, { strokeWidth: value[0] });
      const updatedObj = mapObjectStore.getObjectById(id);
      if (updatedObj) await updateObjectInBackend(updatedObj);
    }
  };

  /**
   * Переключить заливку
   */
  const toggleFill = async (id: string) => {
    const obj = mapObjectStore.Objects.get(id);
    // Не применяем заливку к StopMarker
    if (obj && obj.type !== 'StopMarker') {
      mapObjectStore.updateObjectStyle(id, { filled: !obj.style.filled });
      const updatedObj = mapObjectStore.getObjectById(id);
      if (updatedObj) await updateObjectInBackend(updatedObj);
    }
  };

  /**
   * Изменить размер маркера
   */
  const changeRadius = async (value: number[], id: string) => {
    const obj = mapObjectStore.Objects.get(id);
    if (obj && value && value[0]) {
      if (obj.type === 'StopMarker') {
        // Для StopMarker используем getSizeScale (1.0 - 3.0)
        // Слайдер: 5-100 → getSizeScale: 0.5-3.0
        const getSizeScale = Math.max(0.5, Math.min(3.0, value[0] / 30));
        mapObjectStore.updateObjectStyle(id, { radius: value[0], getSizeScale });
        console.log('[useObjectActions] changeRadius для StopMarker:', { 
          radius: value[0], 
          getSizeScale,
          style: mapObjectStore.Objects.get(id)?.style 
        });
      } else {
        mapObjectStore.updateObjectStyle(id, { radius: value[0] });
      }
      const updatedObj = mapObjectStore.getObjectById(id);
      if (updatedObj) await updateObjectInBackend(updatedObj);
    }
  };

  /**
   * Удалить объект
   */
  const delObject = async (id: string) => {
    const success = await deleteObject(id);
    if (success) {
      mapObjectStore.deleteObject(id);
    }
  };

  /**
   * Найти объект на карте (с анимацией полёта)
   */
  const findOnMap = (id: string) => {
    const obj = mapObjectStore.Objects.get(id);
    if (obj && obj.coordinates.length > 0) {
      const coord = obj.coordinates[0];
      if (coord) {
        const [lng, lat] = coord;
        mapStore.updateViewState({ latitude: lat, longitude: lng, zoom: 16 }, true);
      }
    }
  };

  /**
   * Обновление объекта в бэкенде
   */
  const updateObjectInBackend = async (obj: DeckGLObject) => {
    const backendObj = mapObjectStore.convertDeckGLToBackend(obj);
    const result = await updateObject(backendObj);

    if (result?.status !== "success") {
      console.error("[useObjectActions] Ошибка обновления:", result);
    }
  };

  /**
   * Получить координаты для отображения
   */
  const getCoordinates = (obj: DeckGLObject) => {
    return obj.coordinates.map(([lng, lat]) => ({ lat, lng }));
  };

  /**
   * Конвертация dashArray для слайдера
   */
  const getDashValue = (obj: DeckGLObject): number[] => {
    if (!obj.style.strokeDasharray) return [0];
    return [obj.style.strokeDasharray[0] ?? 0];
  };

  return {
    // Actions
    changeColor,
    toggleStroke,
    changeDash,
    changeFillOpacity,
    changeWeight,
    toggleFill,
    changeRadius,
    delObject,
    findOnMap,
    updateObjectInBackend,
    
    // Utilities
    getCoordinates,
    getDashValue,
    
    // Stores
    mapObjectStore,
    mapStore,
  };
};

export default useObjectActions;
