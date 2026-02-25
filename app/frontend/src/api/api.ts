import type { ObjectCreate } from "@/types";
import ObjectController from "@/api/object";
import type { Objects } from "@/store";

type Status = "success" | "failed";

export interface CreateObjectResponse {
  status: Status;
  message: string;
}

export interface UpdateObjectResponse extends CreateObjectResponse {}

export interface GetObjectResponse {
  status: Status;
  obj: ObjectCreate;
}

export interface GetAllObjectsResponse {
  status: Status;
  objects: ObjectCreate[];
}

interface APIObjects {
  create_object: (Obj: ObjectCreate) => Promise<CreateObjectResponse>;
  get_object: (Id: string) => Promise<GetObjectResponse>;
  get_all_objects: () => Promise<GetAllObjectsResponse>;
  delete_object: (Id: string) => Promise<boolean>;
  update_object: (Obj: ObjectCreate) => Promise<UpdateObjectResponse>;
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
