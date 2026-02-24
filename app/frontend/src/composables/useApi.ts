import { ref, readonly } from "vue";
import { api } from "@/api";
import type { Objects } from "@/store";

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
  const createObject = async (Obj: Objects) =>
    await callApi(api.objects.createObject, Obj);

  return {
    // Состояние
    loading: readonly(loading),
    error: readonly(error),
    // Методы
    createObject,
  };
};

export default useApi;
