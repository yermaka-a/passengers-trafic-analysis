import { defineStore } from "pinia";
import { v6 as uuidv6 } from "uuid";
import useApi from "@/composables/useApi";
import type { BackendObjectCreate, DeckGLObject, LngLatTuple } from "@/types";
import type { StopMarkerType } from "@/config/stopMarkers";
import {
  backendCoordsToDeckGL,
  deckGLToBackendCoords,
  hexToRGBA,
  rgbaToHex,
} from "@/utils";
import { DeckGLMapConfig } from "@/config/DeckGLMapConfig";

// ============================================================================
// ТИПЫ
// ============================================================================

const ObjectsTypes = [
  ["Polygon", "Полигон"],
  ["Polyline", "Полилайн"],
  ["CircleMarker", "Маркер-круг"],
  ["StopMarker", "Маркер"],
  ["Edit", "Редактировать объект"],
] as const;

export type ObjTypes = (typeof ObjectsTypes)[number][0];
export type ObjNames = (typeof ObjectsTypes)[number][1];

/** Временный объект в процессе создания */
export interface DraftObject {
  type: ObjTypes;
  coordinates: LngLatTuple[];
  style: DeckGLObject["style"];
}

interface MapObjectStoreState {
  Objects: Map<string, DeckGLObject>;
  ObjectsTypes: typeof ObjectsTypes;
  ChosenObjectType: (typeof ObjectsTypes)[number];
  DraftObject: DraftObject | null;
  EditingObjectId: string | null;
  ClickedObjId: string | null;
  // Хранение последнего состояния обводки (всегда хранит фактические значения из БД)
  strokeState: Map<
    string,
    { strokeWidth: number; strokeDasharray?: [number, number] }
  >;
  // Фильтры видимости для StopMarker
  visibleStopMarkerTypes: Set<string>;
}

// ============================================================================
// КОНВЕРТАЦИЯ: Backend ↔ Deck.gl
// ============================================================================

/**
 * Конвертирует объект из формата бэкенда в DeckGLObject
 * Инициализирует strokeState фактическими значениями из БД
 */
const backendToDeckGL = (
  backendObj: BackendObjectCreate,
  id?: string,
): DeckGLObject => {
  const { latlng, options } = backendObj;

  // Конвертируем координаты: [{lat, lng}] → [[lng, lat]]
  const coordinates = backendCoordsToDeckGL(latlng);

  // Конвертируем цвет из hex в RGBA
  const color = hexToRGBA(options.color ?? "#0080FF", 255);

  // Инициализируем strokeState фактическими значениями из БД
  if (id) {
    const mapObjectStore = useMapObjectStore();
    mapObjectStore.strokeState.set(id, {
      strokeWidth: options.weight ?? 2,
      strokeDasharray: options.dashArray as [number, number] | undefined,
    });
  }

  return {
    id: options.Id,
    type: options.objType,
    name: options.name,
    customName: options.customName ?? undefined,
    description: options.description ?? undefined,
    style: {
      color,
      strokeWidth: options.stroke ? (options.weight ?? 2) : 0,
      strokeDasharray: options.dashArray as [number, number] | undefined,
      filled: options.fill ?? false,
      fillOpacity: options.fillOpacity ?? 0.5,
      // Для StopMarker/CircleMarker восстанавливаем radius и вычисляем getSizeScale
      ...((options.objType === 'StopMarker' || options.objType === 'CircleMarker') && {
        radius: (options as any).radius ?? 30,
        ...(options.objType === 'StopMarker' && {
          getSizeScale: Math.max(0.5, Math.min(3.0, ((options as any).radius ?? 30) / 30)),
        }),
      }),
    },
    coordinates,
    // Для StopMarker
    markerType: (options as any).markerType ?? undefined,
  };
};

/**
 * Конвертирует DeckGLObject в формат для бэкенда
 * Использует strokeState для получения фактических значений
 */
const deckGLToBackend = (obj: DeckGLObject): BackendObjectCreate => {
  const mapObjectStore = useMapObjectStore();
  const state = mapObjectStore.strokeState.get(obj.id);

  // Конвертируем координаты обратно: [[lng, lat]] → [{lat, lng}]
  const latlng = deckGLToBackendCoords(obj.coordinates);

  // Конвертируем цвет из RGBA в hex (используем color)
  const color = rgbaToHex(obj.style.color ?? [0, 128, 255, 255]);

  // Для StopMarker не используем stroke/fill свойства
  const isStopMarker = obj.type === 'StopMarker';
  const isCircleMarker = obj.type === 'CircleMarker';

  // Используем значения из strokeState (кроме StopMarker)
  const weight = isStopMarker ? undefined : (state?.strokeWidth ?? obj.style.strokeWidth);
  const dashArray = isStopMarker ? undefined : (state?.strokeDasharray ?? obj.style.strokeDasharray);

  return {
    latlng,
    options: {
      Id: obj.id,
      name: obj.name,
      objType: obj.type,
      description: obj.description ?? null,
      color,
      stroke: isStopMarker ? undefined : ((obj.style.strokeWidth ?? 0) > 0),
      weight: weight,
      fill: isStopMarker ? undefined : (obj.style.filled ?? false),
      fillOpacity: isStopMarker ? undefined : (obj.style.fillOpacity ?? 0.5),
      dashArray: dashArray ? Array.from(dashArray) : undefined,
      markerType: obj.markerType ?? null, // Для StopMarker
      radius: (isStopMarker || isCircleMarker) ? (obj.style.radius ?? 30) : undefined, // Для StopMarker/CircleMarker
    },
  };
};

// ============================================================================
// FACTORY ФУНКЦИИ
// ============================================================================

/**
 * Создаёт новый DeckGLObject по типу
 */

// ============================================================================
// STORE
// ============================================================================

export const useMapObjectStore = defineStore("mapobjects", {
  state: (): MapObjectStoreState => ({
    Objects: new Map(),
    ObjectsTypes,
    ChosenObjectType: ObjectsTypes[0] as typeof ObjectsTypes[number],
    DraftObject: null,
    EditingObjectId: null,
    ClickedObjId: null,
    strokeState: new Map(),
    visibleStopMarkerTypes: new Set(['pin', 'pinned', 'flag', 'flag-check', 'pin-check', 'pin-plus', 'balloon']),
  }),

  getters: {
    /** Все объекты на карте */
    getObjects: (state) => state.Objects,

    /** Список типов объектов */
    getObjectsTypes: (state) => state.ObjectsTypes,

    /** Выбранный тип объекта для создания */
    getChosenObjectType: (state) => state.ChosenObjectType,

    /** Текущий создаваемый объект (draft) */
    getDraftObject: (state) => state.DraftObject,

    /** Редактируемый объект */
    getEditingObject: (state) =>
      state.EditingObjectId ? state.Objects.get(state.EditingObjectId) : null,

    /** ID кликнутого объекта */
    getClickedObjId: (state) => state.ClickedObjId,
    
    /** Получить видимые типы маркеров */
    getVisibleStopMarkerTypes: (state) => state.visibleStopMarkerTypes,
  },

  actions: {
    // ========================================================================
    // УПРАВЛЕНИЕ ТИПОМ ОБЪЕКТА
    // ========================================================================

    /** Установить тип создаваемого объекта и синхронизировать через Python API */
    setObjectType(option: (typeof ObjectsTypes)[number]) {
      this.$state.ChosenObjectType = option;
      
      // Синхронизация через Python API
      if (typeof window !== 'undefined' && (window as any).pywebview?.api?.objects) {
        (window as any).pywebview.api.objects.set_object_type(option)
          .then(() => {
            console.log('[MapObjectStore] Chosen type synced via Python API:', option);
          })
          .catch((err: Error) => {
            console.error('[MapObjectStore] Error syncing chosen type:', err);
          });
      }
    },

    // ========================================================================
    // СОЗДАНИЕ ОБЪЕКТОВ (DRAFT)
    // ========================================================================

    /** Начать создание нового объекта */
    startDraftObject(markerType?: StopMarkerType) {
      const type = this.ChosenObjectType[0] as ObjTypes;
      if (type === "Edit") return;

      this.DraftObject = {
        type: type as Exclude<ObjTypes, "Edit">,
        coordinates: [],
        style: {
          ...DeckGLMapConfig.defaultStyles[type as Exclude<ObjTypes, "Edit">],
        } as DeckGLObject["style"],
        // Для StopMarker сохраняем тип маркера
        ...(type === 'StopMarker' && { markerType: markerType || 'bus' }),
      };
    },

    /** Добавить координату к draft объекту */
    addCoordinateToDraft(coord: LngLatTuple) {
      if (!this.DraftObject) return;

      // Для CircleMarker заменяем координату (только одна точка)
      if (this.DraftObject.type === "CircleMarker") {
        this.DraftObject.coordinates = [coord];
      } else {
        this.DraftObject.coordinates.push(coord);
      }
    },

    /** Установить координаты draft объекта (для undo/redo) */
    setDraftCoordinates(coords: LngLatTuple[]) {
      if (!this.DraftObject) return;
      this.DraftObject.coordinates = [...coords];
    },

    /** Обновить стиль draft объекта */
    updateDraftStyle(style: Partial<DeckGLObject["style"]>) {
      if (!this.DraftObject) return;
      this.DraftObject.style = { ...this.DraftObject.style, ...style };
    },

    /** Завершить создание draft объекта */
    finalizeDraftObject(draftColor?: string): DeckGLObject | null {
      if (!this.DraftObject || this.DraftObject.coordinates.length === 0) {
        return null;
      }

      let coordinates = [...this.DraftObject.coordinates];

      // Для полигона замыкаем контур - добавляем первую точку в конец
      if (this.DraftObject.type === "Polygon" && coordinates.length >= 3) {
        const firstCoord = coordinates[0]!;
        coordinates = [...coordinates, firstCoord];
      }

      // Если передан цвет, используем его, иначе берём из draft
      const finalStyle = draftColor
        ? { ...this.DraftObject.style, color: hexToRGBA(draftColor) }
        : { ...this.DraftObject.style };

      // Создаём объект с координатами и стилем
      const newObject: DeckGLObject = {
        id: uuidv6(),
        type: this.DraftObject.type as Exclude<ObjTypes, "Edit">,
        name: ObjectsTypes.find(([key]) => key === this.DraftObject?.type)?.[1] ?? (this.DraftObject?.type as ObjNames),
        style: finalStyle,
        coordinates,
        // Для StopMarker
        ...(this.DraftObject.type === 'StopMarker' && {
          markerType: (this.DraftObject as any).markerType || 'bus',
        }),
      };

      this.Objects.set(newObject.id, newObject);
      const finalized = { ...newObject };
      this.DraftObject = null;

      return finalized;
    },

    /** Отменить создание объекта */
    cancelDraftObject() {
      this.DraftObject = null;
    },

    // ========================================================================
    // РЕДАКТИРОВАНИЕ
    // ========================================================================

    /** Начать редактирование объекта */
    startEditingObject(id: string) {
      this.EditingObjectId = id;
    },

    /** Завершить редактирование объекта */
    stopEditingObject() {
      this.EditingObjectId = null;
    },

    /** Обновить стиль объекта */
    updateObjectStyle(id: string, style: Partial<DeckGLObject["style"]>) {
      const obj = this.Objects.get(id);
      if (obj) {
        // Обновляем strokeState при изменении strokeWidth или strokeDasharray
        if (
          style.strokeWidth !== undefined ||
          style.strokeDasharray !== undefined
        ) {
          const currentState = this.strokeState.get(id);

          if (style.strokeWidth === 0) {
            // Выключаем обводку - strokeState НЕ меняем, там хранятся фактические значения
            // Просто применяем strokeWidth=0 для отображения
          } else if (style.strokeWidth !== undefined) {
            // Изменяем жирность - обновляем strokeState новым значением
            this.strokeState.set(id, {
              strokeWidth: style.strokeWidth ?? currentState?.strokeWidth ?? 2,
              strokeDasharray:
                style.strokeDasharray ?? currentState?.strokeDasharray,
            });
          } else if (style.strokeDasharray !== undefined) {
            // Изменяем пунктир - обновляем strokeState
            this.strokeState.set(id, {
              strokeWidth:
                currentState?.strokeWidth ?? obj.style.strokeWidth ?? 2,
              strokeDasharray: style.strokeDasharray,
            });
          }
        }

        // Создаём НОВЫЙ объект для реактивности Vue
        const updatedObj: DeckGLObject = {
          ...obj,
          style: { ...obj.style, ...style },
        };
        
        console.log('[useMapObjectStore] updateObjectStyle:', { 
          id, 
          style, 
          newStyle: updatedObj.style,
          radius: updatedObj.style.radius,
          getSizeScale: updatedObj.style.getSizeScale 
        });
        
        this.Objects.set(id, updatedObj);
        
        // Принудительно триггерим реактивность
        this.Objects = new Map(this.Objects);
      }
    },

    /** Переключить видимость обводки (не меняя strokeState) */
    toggleStrokeVisibility(id: string, hide: boolean) {
      const obj = this.Objects.get(id);
      const state = this.strokeState.get(id);
      if (obj && state) {
        // Создаём НОВЫЙ объект для реактивности Vue
        const updatedStyle = hide
          ? { ...obj.style, strokeWidth: 0 }
          : {
              ...obj.style,
              strokeWidth: state.strokeWidth,
              strokeDasharray: state.strokeDasharray,
            };

        const updatedObj: DeckGLObject = {
          ...obj,
          style: updatedStyle,
        };
        this.Objects.set(id, updatedObj);
      }
    },

    /** Обновить координаты объекта */
    updateObjectCoordinates(id: string, coordinates: LngLatTuple[]) {
      const obj = this.Objects.get(id);
      if (obj) {
        // Создаём НОВЫЙ объект с новыми координатами для реактивности
        const updatedObj: DeckGLObject = {
          ...obj,
          coordinates: coordinates.map(c => [c[0], c[1]] as LngLatTuple), // deep clone
        };
        // Удаляем и добавляем заново для триггера реактивности
        this.Objects.delete(id);
        this.Objects.set(id, updatedObj);
      }
    },

    /** Удалить объект из store */
    deleteObject(id: string) {
      // Создаём новую Map для триггера реактивности
      const newObjects = new Map(this.Objects);
      newObjects.delete(id);
      this.Objects = newObjects;
      
      this.strokeState.delete(id);
      if (this.ClickedObjId === id) {
        this.ClickedObjId = null;
      }
      if (this.EditingObjectId === id) {
        this.EditingObjectId = null;
      }
    },

    // ========================================================================
    // API МЕТОДЫ (С КОНВЕРТАЦИЕЙ)
    // ========================================================================

    /** Загрузить все объекты из БД */
    async loadAllObjectsFromDB() {
      console.log("[MapObjectStore] Загрузка объектов из БД...");
      const { getAllObjects } = useApi();
      const backendObjects = await getAllObjects();
      console.log(
        "[MapObjectStore] Получено объектов:",
        backendObjects?.length ?? 0,
      );

      if (backendObjects) {
        this.Objects = new Map();
        this.strokeState = new Map();
        for (const backendObj of backendObjects) {
          const deckGLObj = backendToDeckGL(backendObj, backendObj.options.Id);
          this.Objects.set(deckGLObj.id, deckGLObj);
        }
      }
    },

    /** Сохранить новый объект в БД */
    async saveObjectToDB(obj: DeckGLObject) {
      const { createObject } = useApi();
      const backendObj = deckGLToBackend(obj);
      return await createObject(backendObj);
    },

    /** Обновить объект в БД */
    async updateObjectInDB(obj: DeckGLObject) {
      const { updateObject } = useApi();
      const backendObj = deckGLToBackend(obj);
      return await updateObject(backendObj);
    },

    /** Удалить объект из БД */
    async deleteObjectFromDB(id: string) {
      const { deleteObject } = useApi();
      const success = await deleteObject(id);
      if (success) {
        this.Objects.delete(id);
      }
      return success;
    },

    // ========================================================================
    // ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    // ========================================================================

    /** Получить объект по ID */
    getObjectById(id: string): DeckGLObject | undefined {
      return this.Objects.get(id);
    },

    /** Конвертировать BackendObjectCreate в DeckGLObject (публичный метод) */
    convertBackendToDeckGL(backendObj: BackendObjectCreate): DeckGLObject {
      return backendToDeckGL(backendObj);
    },

    /** Конвертировать DeckGLObject в BackendObjectCreate (публичный метод) */
    convertDeckGLToBackend(obj: DeckGLObject): BackendObjectCreate {
      return deckGLToBackend(obj);
    },
    
    /** Установить видимые типы маркеров */
    setVisibleStopMarkerTypes(types: Set<string>) {
      this.$state.visibleStopMarkerTypes = types;
    },
    
    /** Переключить видимость типа маркера */
    toggleStopMarkerType(type: string) {
      const types = new Set(this.$state.visibleStopMarkerTypes);
      if (types.has(type)) {
        types.delete(type);
      } else {
        types.add(type);
      }
      this.$state.visibleStopMarkerTypes = types;
    },
  },
});
