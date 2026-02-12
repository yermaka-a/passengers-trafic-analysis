import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import { ROUTES } from "./routes";

export const router = createRouter({
  history: createWebHistory(),
  routes: ROUTES as unknown as RouteRecordRaw[],
});
