import { innerAPI } from "@/api/api";
import type { Objects } from "@/store/";
import {
  Polygon,
  Polyline,
  type CircleMarkerOptions,
  type LatLng,
  type PolylineOptions,
} from "leaflet";

export interface ObjectCreate {
  latlng: LatLng[];
  options: PolylineOptions | CircleMarkerOptions;
}

export default class ObjectController {
  createObject = async (Obj: Objects) => {
    if (Obj instanceof Polygon || Obj instanceof Polyline) {
      const newObject: ObjectCreate = {
        latlng: Obj.getLatLngs().flat().flat(),
        options: Obj.options,
      };
      try {
        if (innerAPI.objects) {
          const response = await innerAPI.objects.create_object(newObject);

          if (response.status === "success") {
            return response;
          } else {
            console.error("Pydantic error:", response.message);
            return response;
          }
        }
        throw new Error("pywebview is not registered");
      } catch (err) {
        console.error("bridge error:", err);
        throw err;
      }
    }
  };
}
