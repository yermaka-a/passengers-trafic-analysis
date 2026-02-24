import type { ObjectCreate } from "@/api/object";
import ObjectController from "@/api/object";

export interface CreateObjectResponse {
  status: "success" | "failed";
  message: string;
}

interface APIObjects {
  create_object: (Obj: ObjectCreate) => Promise<CreateObjectResponse>;
}

class API {
  private static api: API | null = null;
  private constructor() {}
  static getAPI() {
    if (API.api === null) {
      API.api = new API();
      return API.api;
    }
    return API.api;
  }

  objects = new ObjectController();
}

const api = API.getAPI();
export default api;

class InnerAPI {
  private static api: InnerAPI | null = null;
  private constructor() {}
  static getAPI() {
    if (InnerAPI.api === null) {
      InnerAPI.api = new InnerAPI();
      return InnerAPI.api;
    }
    return InnerAPI.api;
  }

  get objects() {
    if ((globalThis as any)?.pywebview?.api?.objects) {
      return (globalThis as any).pywebview?.api?.objects as APIObjects;
    }
    console.log("pywebview not registered yet");
    return null;
  }
}
export const innerAPI = InnerAPI.getAPI();
