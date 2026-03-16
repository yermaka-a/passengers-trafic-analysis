import { ref, readonly, computed } from "vue";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import type { LngLatTuple } from "@/types";

/**
 * Composable для управления AntV L7 объектами на карте
 *
 * Обрабатывает:
 * - Создание объектов (Polygon, Polyline, CircleMarker)
 * - Историю undo/redo
 * - Редактирование координат
 */
export const useL7 = () => {
  const mapObjectStore = useMapObjectStore();

  // История для undo/redo
  interface HistoryEntry {
    objectId: string;
    coordinates: LngLatTuple[];
    type: "add" | "update" | "delete";
  }

  const history = ref<HistoryEntry[]>([]);
  const historyIndex = ref(-1);
  const isEditing = ref(false);

  // Вычисляемые свойства для кнопок
  const canUndo = computed(() => historyIndex.value >= 0);
  const canRedo = computed(() => historyIndex.value < history.value.length - 1);

  // Добавление в историю
  const pushToHistory = (entry: HistoryEntry) => {
    // Если мы не в конце истории, обрезаем хвост
    if (historyIndex.value < history.value.length - 1) {
      history.value.splice(historyIndex.value + 1);
    }

    history.value.push({
      ...entry,
      coordinates: JSON.parse(JSON.stringify(entry.coordinates)), // deep clone
    });
    historyIndex.value = history.value.length - 1;
  };

  // Undo
  const undo = () => {
    if (!canUndo.value) return null;

    const entry = history.value[historyIndex.value];
    historyIndex.value--;

    // Восстанавливаем предыдущее состояние
    if (entry && entry.objectId) {
      const prevEntry =
        historyIndex.value >= 0 ? history.value[historyIndex.value] : null;

      if (prevEntry) {
        // Восстанавливаем координаты из предыдущей записи
        mapObjectStore.updateObjectCoordinates(
          entry.objectId,
          prevEntry.coordinates,
        );
      }
    }

    return entry;
  };

  // Redo
  const redo = () => {
    if (!canRedo.value) return null;

    historyIndex.value++;
    const entry = history.value[historyIndex.value];

    if (entry && entry.objectId) {
      mapObjectStore.updateObjectCoordinates(entry.objectId, entry.coordinates);
    }

    return entry;
  };

  // Обработка клика по карте (создание объекта)
  const handleMapClick = (lngLat: LngLatTuple) => {
    const draft = mapObjectStore.getDraftObject;

    if (!draft) {
      // Начинаем создание нового объекта
      mapObjectStore.startDraftObject();
      mapObjectStore.addCoordinateToDraft(lngLat);
    } else {
      // Добавляем точку к существующему draft
      mapObjectStore.addCoordinateToDraft(lngLat);
    }
  };

  // Завершение создания объекта
  const finalizeObject = async () => {
    const finalized = mapObjectStore.finalizeDraftObject();

    if (finalized) {
      // Добавляем в историю
      pushToHistory({
        objectId: finalized.id,
        coordinates: [...finalized.coordinates],
        type: "add",
      });

      // Отправка на бэкенд
      await mapObjectStore.saveObjectToDB(finalized);
    }
  };

  // Отмена создания
  const cancelObject = () => {
    mapObjectStore.cancelDraftObject();
  };

  // Обновление координат объекта (при редактировании)
  const updateObjectCoordinates = (id: string, coordinates: LngLatTuple[]) => {
    mapObjectStore.updateObjectCoordinates(id, coordinates);
  };

  // Начало редактирования
  const startEditing = (id: string) => {
    isEditing.value = true;
    mapObjectStore.startEditingObject(id);
  };

  // Завершение редактирования
  const stopEditing = async () => {
    isEditing.value = false;
    const editingObj = mapObjectStore.getEditingObject;

    if (editingObj) {
      await mapObjectStore.updateObjectInDB(editingObj);
      mapObjectStore.stopEditingObject();
    }
  };

  return {
    // State
    history: readonly(history),
    historyIndex: readonly(historyIndex),
    isEditing: readonly(isEditing),
    canUndo,
    canRedo,

    // Actions
    undo,
    redo,
    handleMapClick,
    finalizeObject,
    cancelObject,
    updateObjectCoordinates,
    pushToHistory,
    startEditing,
    stopEditing,
  };
};

export default useL7;
