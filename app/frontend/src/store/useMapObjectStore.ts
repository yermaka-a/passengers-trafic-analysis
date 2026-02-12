import { defineStore } from "pinia";
import * as L from "leaflet";
import { v6 as uuidv6 } from "uuid";
import type { CircleMarkerOptions, LatLng, PolylineOptions } from "leaflet";

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
interface ObjectCreate {
  latlng: LatLng[];
  options: PolylineOptions | CircleMarkerOptions;
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

// const getObjects = () => {
//   // const ls = localStorage.getItem("objects");
//   // const Objects = new Map();
//   // if (ls) {
//   //   const objects = JSON.parse(ls);
//   //   for (obj of objects){
//   //     Objects.set(obj.options.Id, obj)
//   //   }
//   // }
// };

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
      this.Objects.set(Id, Obj);
      if (Obj instanceof L.Polygon || Obj instanceof L.Polyline) {
        const newObject: ObjectCreate = {
          latlng: Obj.getLatLngs().flat().flat(),
          options: Obj.options,
        };
        try {
          const response = await (
            globalThis as any
          ).pywebview.api.objects.create_object(newObject);

          if (response.status === "success") {
            console.log("Сохранено в SQLite с UUID:", newObject.options.Id);
          } else {
            console.error("Ошибка Pydantic:", response.message);
          }
        } catch (err) {
          console.error("Ошибка моста:", err);
        }
      }
    },
    clearObject() {
      this.MapObject = null;
    },
  },
});
