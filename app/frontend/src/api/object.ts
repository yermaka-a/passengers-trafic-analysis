import { innerAPI } from "@/api/api";
import type { BackendObjectCreate, BackendResponse } from "@/types";

/**
 * ObjectController для работы с бэкендом через pywebview
 *
 * Принимает и возвращает BackendObjectCreate формат:
 * - latlng: [{lat, lng}, ...]
 * - options: { Id, name, objType, color, stroke, weight, fill, fillOpacity, dashArray }
 */
export default class ObjectController {
  /**
   * Создать новый объект
   */
  createObject = async (obj: BackendObjectCreate) => {
    try {
      if (innerAPI.objects) {
        const response = await innerAPI.objects.create_object(obj);
        return response as BackendResponse;
      }
      throw new Error("pywebview is not registered");
    } catch (err) {
      console.error("API Error:", err);
      throw err;
    }
  };

  /**
   * Получить объект по ID
   */
  getObject = async (id: string) => {
    try {
      if (innerAPI.objects) {
        const response = await innerAPI.objects.get_object(id);
        return response as BackendResponse;
      }
      throw new Error("pywebview is not registered");
    } catch (err) {
      console.error("API Error:", err);
      throw err;
    }
  };

  /**
   * Получить все объекты
   * @returns Массив объектов в формате BackendObjectCreate
   */
  getAllObjects = async () => {
    try {
      if (innerAPI.objects) {
        const response = await innerAPI.objects.get_all_objects();
        if (response.status === "success") {
          return response.objects as BackendObjectCreate[];
        }
        return null;
      }
      throw new Error("pywebview is not registered");
    } catch (err) {
      console.error("API Error:", err);
      throw err;
    }
  };

  /**
   * Удалить объект по ID
   * @returns true если успешно
   */
  deleteObject = async (id: string): Promise<boolean> => {
    try {
      if (innerAPI.objects) {
        return await innerAPI.objects.delete_object(id);
      }
      throw new Error("pywebview is not registered");
    } catch (err) {
      console.error("API Error:", err);
      return false;
    }
  };

  /**
   * Обновить объект
   */
  updateObject = async (obj: BackendObjectCreate) => {
    try {
      if (innerAPI.objects) {
        const response = await innerAPI.objects.update_object(obj);
        return response as BackendResponse;
      }
      throw new Error("pywebview is not registered");
    } catch (err) {
      console.error("API Error:", err);
      throw err;
    }
  };
}
