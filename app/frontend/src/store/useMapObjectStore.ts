import { defineStore } from "pinia";
import * as L from "leaflet";
import { v6 as uuidv6 } from "uuid";
import { useApi } from "@/composables";
import { useMapStore } from "@/store/useMapStore";
import type { ObjectCreate } from "@/types";

export class ObjectEditor {}
export type Objects = L.Polygon | L.Polyline | L.CircleMarker;
// Добавление только в конец элементов
const ObjectsTypes = [
  ["Polygon", "Полигон"],
  ["Polyline", "Полилайн"],
  ["CircleMarker", "Маркер"],
  ["Edit", "Редактировать объект"],
] as const;
export type ObjTypes = (typeof ObjectsTypes)[number][0];
export type ObjNames = (typeof ObjectsTypes)[number][1];
interface MapObjectStore {
  Objects: Map<string, Objects> | null;
  ObjectsTypes: typeof ObjectsTypes;
  ChosenObjectType: (typeof ObjectsTypes)[number];
  // Текущий создающийся объект карты
  MapObject: Objects | ObjectEditor | null;
  ClickedObjId: string | null;
}

const setId = (e: L.LeafletMouseEvent, store: MapObjectStore) => {
  if (e.sourceTarget.options.Id) {
    store.ClickedObjId = e.sourceTarget.options.Id;
    console.log(e.sourceTarget.options.Id);
  }
};

const getMapObjectByType = (
  store: MapObjectStore,
  ChosenObjectType: (typeof ObjectsTypes)[number],
) => {
  switch (ChosenObjectType[0]) {
    case ObjectsTypes[0][0]: {
      const polygon = new L.Polygon([], {
        Id: uuidv6(),
        objType: "Polygon",
        name: "Полигон",
      });
      polygon.on("click", (e) => setId(e, store));
      return polygon;
    }
    case ObjectsTypes[1][0]: {
      const polyline = new L.Polyline([], {
        Id: uuidv6(),
        objType: "Polyline",
        name: "Полилайн",
      });
      polyline.on("click", (e) => setId(e, store));
      return polyline;
    }
    case ObjectsTypes[2][0]: {
      const circleMarker = new L.CircleMarker([0, 0], {
        Id: uuidv6(),
        objType: "CircleMarker",
        name: "Круговой маркер",
      });
      circleMarker.on("click", (e) => setId(e, store));
      return circleMarker;
    }
    case ObjectsTypes[3][0]:
      return new ObjectEditor();
  }
};

const createObjByTypeName: Record<
  Exclude<ObjTypes, "Edit">,
  (objType: ObjectCreate, store: MapObjectStore) => Objects
> = {
  Polygon: (obj, store) => {
    const polygon = new L.Polygon(obj.latlng, { ...obj.options });
    polygon.on("click", (e) => setId(e, store));
    return polygon;
  },
  Polyline: (obj, store): L.Polyline => {
    const polyline = new L.Polyline(obj.latlng, { ...obj.options });
    polyline.on("click", (e) => setId(e, store));
    return polyline;
  },
  CircleMarker: (obj, store): L.CircleMarker => {
    const circleMarker = new L.CircleMarker(obj.latlng as L.LatLngExpression, {
      ...obj.options,
    });
    circleMarker.on("click", (e) => setId(e, store));
    return circleMarker;
  },
};

export const useMapObjectStore = defineStore("mapobjects", {
  state: (): MapObjectStore => {
    return {
      Objects: null,
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
    async loadAllObjectsFromDB() {
      if (!this.Objects) {
        this.Objects = new Map();
        const { getAllObjects } = useApi();
        const objects = await getAllObjects();
        if (objects) {
          console.log("all objects from db:", objects);
          const mapStore = useMapStore();
          for (const obj of objects) {
            if (mapStore.getMapRef) {
              const newObj = createObjByTypeName[obj.options.objType](
                obj,
                this as unknown as MapObjectStore,
              );
              // TODO Переделать проверку на карту на хук
              if (mapStore.mapInstance)
                newObj.addTo(mapStore.mapInstance as L.Map);
              this.Objects.set(newObj.options.Id, newObj);
            }
          }
        }
        return;
      }
      return this.Objects;
    },
    setObjectType(option: (typeof ObjectsTypes)[number]) {
      this.$state.ChosenObjectType = option;
    },
    getObjectByChosenType() {
      return getMapObjectByType(
        this as unknown as MapObjectStore,
        this.ChosenObjectType,
      );
    },
    async setObject(Obj: Objects) {
      const Id = Obj.options.Id;
      const { createObject } = useApi();
      const objResponse = await createObject(Obj);
      if (this.Objects) this.Objects.set(Id, Obj);
      return objResponse;
    },
    clearObject() {
      this.MapObject = null;
    },
  },
});
