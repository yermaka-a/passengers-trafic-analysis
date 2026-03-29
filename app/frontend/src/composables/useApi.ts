import { ref, readonly } from "vue";
import { api } from "@/api";
import type { BackendObjectCreate } from "@/types";

const useApi = () => {
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function callApi<A, T>(
    apiMethod: (...args: A[]) => Promise<T>,
    ...args: A[]
  ) {
    loading.value = true;
    error.value = null;

    try {
      const result = await apiMethod(...args);
      return result;
    } catch (err) {
      error.value = (err as Error).message;
      console.error("API Error:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Конкретные методы с состоянием
  const createObject = async (obj: BackendObjectCreate) =>
    await callApi(api.objects.createObject, obj);

  const getObject = async (id: string) =>
    await callApi(api.objects.getObject, id);

  const getAllObjects = async () => await callApi(api.objects.getAllObjects);

  const updateObject = async (obj: BackendObjectCreate) =>
    await callApi(api.objects.updateObject, obj);

  const deleteObject = async (id: string) =>
    await callApi(api.objects.deleteObject, id);

  // Tile layers
  const getCurrentTileLayer = async (): Promise<{ status: string; layer: string }> =>
    await callApi(api.tile_layers.getCurrentLayer);

  const setCurrentTileLayer = async (layer: string): Promise<{ status: string; layer: string }> =>
    await callApi(api.tile_layers.setCurrentLayer, layer);

  // Импорт остановок из Overpass API
  const importStopsFromOverpass = async (cities: string, types: string[]) => {
    loading.value = true;
    error.value = null;
    
    try {
      // Проверка что pywebview доступен
      if (!(window as any).pywebview?.api?.import_stops) {
        throw new Error('pywebview.api.import_stops недоступен. Убедитесь что приложение запущено через pywebview.');
      }
      
      console.log('[useApi] Вызов import_stops:', { cities, types });
      const result = await (window as any).pywebview.api.import_stops({
        cities,
        stop_types: types
      });
      console.log('[useApi] import_stops результат:', result);
      return result;
    } catch (err) {
      error.value = (err as Error).message;
      console.error("API Error:", err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    // Состояние
    loading: readonly(loading),
    error: readonly(error),
    // Методы
    createObject,
    getObject,
    getAllObjects,
    updateObject,
    deleteObject,
    getCurrentTileLayer,
    setCurrentTileLayer,
    importStopsFromOverpass,
  };
};

export default useApi;
