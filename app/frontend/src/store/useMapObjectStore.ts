import { defineStore } from "pinia";
import { v6 as uuidv6 } from "uuid";
import useApi from "@/composables/useApi";
import type { BackendObjectCreate, L7Object, LngLatTuple } from "@/types";
import {
  backendCoordsToL7,
  l7ToBackendCoords,
  hexToRGBA,
  rgbaToHex,
} from "@/utils";
import { L7MapConfig } from "@/config/L7MapConfig";

// ============================================================================
// ТИПЫ
// ============================================================================

const ObjectsTypes = [
  ["Polygon", "Полигон"],
  ["Polyline", "Полилайн"],
  ["CircleMarker", "Маркер"],
  ["Edit", "Редактировать объект"],
] as const;

export type ObjTypes = (typeof ObjectsTypes)[number][0];
export type ObjNames = (typeof ObjectsTypes)[number][1];

/** Временный объект в процессе создания */
export interface DraftObject {
  type: ObjTypes;
  coordinates: LngLatTuple[];
  style: L7Object["style"];
}

interface MapObjectStoreState {
  Objects: Map<string, L7Object>;
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
}

// ============================================================================
// КОНВЕРТАЦИЯ: Backend ↔ L7
// ============================================================================

/**
 * Конвертирует объект из формата бэкенда в L7Object
 * Инициализирует strokeState фактическими значениями из БД
 */
const backendToL7 = (
  backendObj: BackendObjectCreate,
  id?: string,
): L7Object => {
  const { latlng, options } = backendObj;

  // Конвертируем координаты: [{lat, lng}] → [[lng, lat]]
  const coordinates = backendCoordsToL7(latlng);

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
      fillColor: color,
      strokeColor: color,
      strokeWidth: options.stroke ? (options.weight ?? 2) : 0,
      strokeDasharray: options.dashArray as [number, number] | undefined,
      filled: options.fill ?? false,
      fillOpacity: options.fillOpacity ?? 0.5,
    },
    coordinates,
  };
};

/**
 * Конвертирует L7Object в формат для бэкенда
 * Использует strokeState для получения фактических значений
 */
const l7ToBackend = (obj: L7Object): BackendObjectCreate => {
  const mapObjectStore = useMapObjectStore();
  const state = mapObjectStore.strokeState.get(obj.id);

  // Конвертируем координаты обратно: [[lng, lat]] → [{lat, lng}]
  const latlng = l7ToBackendCoords(obj.coordinates);

  // Конвертируем цвет из RGBA в hex (используем fillColor)
  const color = rgbaToHex(
    obj.style.fillColor ?? obj.style.strokeColor ?? [0, 128, 255, 255],
  );

  // Используем значения из strokeState
  const weight = state?.strokeWidth ?? obj.style.strokeWidth;
  const dashArray = state?.strokeDasharray ?? obj.style.strokeDasharray;

  return {
    latlng,
    options: {
      Id: obj.id,
      name: obj.name,
      objType: obj.type,
      customName: obj.customName ?? null,
      description: obj.description ?? null,
      color,
      stroke: obj.style.strokeWidth > 0, // Флаг включённости обводки
      weight: weight, // Фактическая жирность из strokeState
      fill: obj.style.filled,
      fillOpacity: obj.style.fillOpacity,
      dashArray: dashArray ? Array.from(dashArray) : null, // Фактический пунктир из strokeState
    },
  };
};

// ============================================================================
// FACTORY ФУНКЦИИ
// ============================================================================

/**
 * Создаёт новый L7Object по типу
 */
const createNewL7Object = (
  type: Exclude<ObjTypes, "Edit">,
  coordinates: LngLatTuple[],
): L7Object => {
  const defaultStyle = L7MapConfig.defaultStyles[type];

  return {
    id: uuidv6(),
    type,
    name: ObjectsTypes.find(([key]) => key === type)?.[1] ?? type,
    style: { ...defaultStyle } as L7Object["style"],
    coordinates,
  };
};

// ============================================================================
// STORE
// ============================================================================

export const useMapObjectStore = defineStore("mapobjects", {
  state: (): MapObjectStoreState => ({
    Objects: new Map(),
    ObjectsTypes,
    ChosenObjectType: ObjectsTypes[0],
    DraftObject: null,
    EditingObjectId: null,
    ClickedObjId: null,
    strokeState: new Map(),
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
  },

  actions: {
    // ========================================================================
    // УПРАВЛЕНИЕ ТИПОМ ОБЪЕКТА
    // ========================================================================

    /** Установить тип создаваемого объекта */
    setObjectType(option: (typeof ObjectsTypes)[number]) {
      this.$state.ChosenObjectType = option;
    },

    // ========================================================================
    // СОЗДАНИЕ ОБЪЕКТОВ (DRAFT)
    // ========================================================================

    /** Начать создание нового объекта */
    startDraftObject() {
      const type = this.ChosenObjectType[0] as ObjTypes;
      if (type === "Edit") return;

      this.DraftObject = {
        type: type as Exclude<ObjTypes, "Edit">,
        coordinates: [],
        style: {
          ...L7MapConfig.defaultStyles[type as Exclude<ObjTypes, "Edit">],
        } as L7Object["style"],
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

    /** Завершить создание draft объекта */
    finalizeDraftObject(): L7Object | null {
      if (!this.DraftObject || this.DraftObject.coordinates.length === 0) {
        return null;
      }

      let coordinates = [...this.DraftObject.coordinates];

      // Для полигона замыкаем контур - добавляем первую точку в конец
      if (this.DraftObject.type === "Polygon" && coordinates.length >= 3) {
        const firstCoord = coordinates[0]!;
        coordinates = [...coordinates, firstCoord];
      }

      const newObject = createNewL7Object(
        this.DraftObject.type as Exclude<ObjTypes, "Edit">,
        coordinates,
      );

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
    updateObjectStyle(id: string, style: Partial<L7Object["style"]>) {
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
              strokeWidth: style.strokeWidth,
              strokeDasharray:
                style.strokeDasharray ?? currentState?.strokeDasharray,
            });
          } else if (style.strokeDasharray !== undefined) {
            // Изменяем пунктир - обновляем strokeState
            this.strokeState.set(id, {
              strokeWidth: currentState?.strokeWidth ?? obj.style.strokeWidth,
              strokeDasharray: style.strokeDasharray,
            });
          }
        }

        obj.style = { ...obj.style, ...style };
        this.Objects.set(id, obj);
      }
    },

    /** Переключить видимость обводки (не меняя strokeState) */
    toggleStrokeVisibility(id: string, hide: boolean) {
      const obj = this.Objects.get(id);
      const state = this.strokeState.get(id);
      if (obj && state) {
        if (hide) {
          // Выключаем обводку - просто ставим 0, strokeState не трогаем
          obj.style.strokeWidth = 0;
        } else {
          // Включаем обводку - восстанавливаем из strokeState
          obj.style.strokeWidth = state.strokeWidth;
          obj.style.strokeDasharray = state.strokeDasharray;
        }
        this.Objects.set(id, obj);
      }
    },

    /** Обновить координаты объекта */
    updateObjectCoordinates(id: string, coordinates: LngLatTuple[]) {
      const obj = this.Objects.get(id);
      if (obj) {
        obj.coordinates = coordinates;
        this.Objects.set(id, obj);
      }
    },

    /** Удалить объект из store */
    deleteObject(id: string) {
      this.Objects.delete(id);
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
          const l7Obj = backendToL7(backendObj, backendObj.options.Id);
          this.Objects.set(l7Obj.id, l7Obj);
        }
        console.log(
          "[MapObjectStore] Загружено объектов в store:",
          this.Objects.size,
        );
      }
    },

    /** Сохранить новый объект в БД */
    async saveObjectToDB(obj: L7Object) {
      const { createObject } = useApi();
      const backendObj = l7ToBackend(obj);
      return await createObject(backendObj);
    },

    /** Обновить объект в БД */
    async updateObjectInDB(obj: L7Object) {
      const { updateObject } = useApi();
      const backendObj = l7ToBackend(obj);
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
    getObjectById(id: string): L7Object | undefined {
      return this.Objects.get(id);
    },

    /** Конвертировать BackendObjectCreate в L7Object (публичный метод) */
    convertBackendToL7(backendObj: BackendObjectCreate): L7Object {
      return backendToL7(backendObj);
    },

    /** Конвертировать L7Object в BackendObjectCreate (публичный метод) */
    convertL7ToBackend(obj: L7Object): BackendObjectCreate {
      return l7ToBackend(obj);
    },
  },
});
