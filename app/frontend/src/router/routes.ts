import Main from "@/pages/Main.vue";
import MapPanel from "@/components/MapPanel/MapPanel.vue";
import type { RouteRecordRaw } from "vue-router";

type AppRouteRecord = Omit<RouteRecordRaw, "name" | "children"> & {
  name: string;
  children?: readonly AppRouteRecord[];
};

type GetRouteName<T extends AppRouteRecord> = T extends {
  children: readonly AppRouteRecord[];
}
  ? T["name"] | GetRoutesNames<T["children"]>
  : T["name"];

type GetRoutesNames<T extends readonly AppRouteRecord[]> = GetRouteName<
  T[number]
>;

export const ROUTES = [
  {
    name: "home",
    path: "/",
    component: Main,
    children: [
      {
        name: "main",
        path: "",
        component: MapPanel,
      },
    ],
  },
  // Отдельные страницы для окон (ленивая загрузка)
  {
    name: "map",
    path: "/map",
    component: () => import("@/pages/MapOnly.vue"),
  },
  {
    name: "list",
    path: "/list",
    component: () => import("@/pages/ListOnly.vue"),
  },
  {
    name: "brush",
    path: "/brush",
    component: () => import("@/pages/BrushTableOnly.vue"),
  },
] as const satisfies readonly AppRouteRecord[];
