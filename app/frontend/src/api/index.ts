import { APIConfig } from "@/config";

// Установка токена (будет вызвана при инициализации)
export function setToken() {
  console.log(
    "token from pywebview:",
    (globalThis as any).token,
    (globalThis as any).pywebview.token,
  );
}

async function apiRequest(endpoint: string, data: object = {}) {
  try {
    const response = await fetch(`${APIConfig.API_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...data,
        token: APIConfig.API_TOKEN,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API Request failed:", error);
    throw error;
  }
}

// Конкретные методы API
export const api = {
  // Инициализация
  async initialize() {
    return apiRequest("/init");
  },

  // Выбор папки
  async choosePath() {
    return apiRequest("/choose/path");
  },

  // Полноэкранный режим
  async toggleFullscreen() {
    return apiRequest("/fullscreen");
  },

  // // Открытие ссылки
  // async openUrl(url) {
  //   return apiRequest("/open-url", { url });
  // },

  // Основная логика
  async doStuff(data: object) {
    return apiRequest("/do/stuff", data);
  },
};
