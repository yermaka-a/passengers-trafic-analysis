import type { BackendObjectCreate } from "@/types";
import ObjectController from "@/api/object";

type Status = "success" | "failed";

export interface CreateObjectResponse {
  status: Status;
  message: string;
}

export interface UpdateObjectResponse extends CreateObjectResponse {}

export interface GetObjectResponse {
  status: Status;
  obj: BackendObjectCreate;
}

export interface GetAllObjectsResponse {
  status: Status;
  objects: BackendObjectCreate[];
}

interface APIObjects {
  create_object: (obj: BackendObjectCreate) => Promise<CreateObjectResponse>;
  get_object: (Id: string) => Promise<GetObjectResponse>;
  get_all_objects: () => Promise<GetAllObjectsResponse>;
  delete_object: (Id: string) => Promise<boolean>;
  update_object: (obj: BackendObjectCreate) => Promise<UpdateObjectResponse>;
}

type LEVEL = "ERROR" | "WARN" | "INFO" | "DEBUG";
export interface Logs {
  level: LEVEL;
  msg: string;
  extraInfo: object;
}

interface APILogs {
  write_log: (logs: Logs) => void;
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

  get logs() {
    if ((globalThis as any)?.pywebview?.api?.logs) {
      return (globalThis as any).pywebview?.api?.logs as APILogs;
    }
    console.log("pywebview not registered yet");
    return null;
  }
}
export const innerAPI = InnerAPI.getAPI();
