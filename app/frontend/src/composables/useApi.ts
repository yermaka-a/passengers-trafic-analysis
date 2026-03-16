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
  };
};

export default useApi;
