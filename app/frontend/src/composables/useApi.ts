import { ref, readonly } from "vue";
import { api, setToken } from "@/api";

export function useApi() {
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Метод-обёртка с обработкой состояния
  async function callApi<A>(apiMethod: Function, ...args: A[]) {
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
  const initializeApp = async () => callApi(api.initialize);
  const chooseFolder = async () => callApi(api.choosePath);
  const toggleFs = async () => callApi(api.toggleFullscreen);
  // const openExternal = async (url: string) => callApi(api.openUrl, url);
  const performAction = async (data: object) => callApi(api.doStuff, data);

  return {
    // Состояние
    loading: readonly(loading),
    error: readonly(error),

    // Методы
    initializeApp,
    chooseFolder,
    toggleFs,
    // openExternal,
    performAction,

    // Утилиты
    setToken,
  };
}
