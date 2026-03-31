import {
  createRouter,
  createWebHashHistory,
  type RouteRecordRaw,
} from "vue-router";
import { ROUTES } from "./routes";

export const router = createRouter({
  history: createWebHashHistory(),
  routes: ROUTES as unknown as RouteRecordRaw[],
});
