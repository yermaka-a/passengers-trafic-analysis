import Main from "@/pages/Main.vue";
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
    path: "/home",
    component: Main,
  },
  //   children: [
  //     { name: "orderId", path: ":orderId", component: OrderCard },
  //     {
  //       name: "user",
  //       path: "user",
  //       component: UserCard,
  //     },
  //     {
  //       name: "techno",
  //       path: "techno",
  //       component: MainTable,
  //     },
  //     {
  //       name: "pass",
  //       path: "pass",
  //       component: PassTable,
  //     },
  //   ],
  // },
  // { name: "root", path: "/", redirect: "/home" },
] as const satisfies readonly AppRouteRecord[];
