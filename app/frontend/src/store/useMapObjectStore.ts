import { defineStore } from "pinia";
import * as L from "leaflet";
import { v6 as uuidv6 } from "uuid";
import { useApi } from "@/composables";

declare module "leaflet" {
  interface PolylineOptions {
    Id: string;
    order: number;
    name: string;
    CustomName?: string;
    description?: string;
  }
  interface CircleMarkerOptions {
    Id: string;
    order: number;
    name: string;
    CustomName?: string;
    description?: string;
  }
}

export class ObjectEditor {}
export type Objects = L.Polygon | L.Polyline | L.CircleMarker;
// Добавление только в конец элементов
const ObjectsTypes = [
  ["Polygon", "Полигон"],
  ["Polyline", "Полилайн"],
  ["CircleMarker", "Маркер"],
  ["Edit", "Редактировать объект"],
] as const;
interface MapObjectStore {
  Objects: Map<string, Objects>;
  ObjectsCount: number;
  ObjectsTypes: typeof ObjectsTypes;
  ChosenObjectType: (typeof ObjectsTypes)[number];
  MapObject: Objects | ObjectEditor | null;
  ClickedObjId: string | null;
}

export const useMapObjectStore = defineStore("mapobjects", {
  state: (): MapObjectStore => {
    return {
      Objects: new Map<string, Objects>(),
      ObjectsCount: 0,
      ObjectsTypes: ObjectsTypes,
      ChosenObjectType: ObjectsTypes[0],
      MapObject: null,
      ClickedObjId: null,
    };
  },
  getters: {
    getObjects: (state) => state.Objects,
    getObjectsTypes: (state) => state.ObjectsTypes,
    getChosenObjectType: (state) => state.ChosenObjectType,
  },
  actions: {
    setObjectType(option: (typeof ObjectsTypes)[number]) {
      this.$state.ChosenObjectType = option;
    },
    getObjectByChosenType() {
      if (this.ChosenObjectType[0] !== "Edit") this.$state.ObjectsCount++;
      const setId = (e: L.LeafletMouseEvent) => {
        if (e.sourceTarget.options.Id) {
          this.ClickedObjId = e.sourceTarget.options.Id;
        }
      };
      const order = this.$state.ObjectsCount;
      switch (this.ChosenObjectType[0]) {
        case ObjectsTypes[0][0]: {
          const polygon = new L.Polygon([], {
            Id: uuidv6(),
            order,
            name: "Полигон",
          });
          polygon.on("click", setId);
          return polygon;
        }
        case ObjectsTypes[1][0]: {
          const polyline = new L.Polyline([], {
            Id: uuidv6(),
            order,
            name: "Полилайн",
          });
          polyline.on("click", setId);
          return polyline;
        }
        case ObjectsTypes[2][0]: {
          const circleMarker = new L.CircleMarker([0, 0], {
            Id: uuidv6(),
            order,
            name: "Круговой маркер",
          });
          circleMarker.on("click", setId);
          return circleMarker;
        }
        case ObjectsTypes[3][0]:
          return new ObjectEditor();
      }
    },
    async setObject(Obj: Objects) {
      const Id = Obj.options.Id;
      const { createObject } = useApi();
      const objResponse = await createObject(Obj);
      this.Objects.set(Id, Obj);
      return objResponse;
    },
    clearObject() {
      this.MapObject = null;
    },
  },
});
