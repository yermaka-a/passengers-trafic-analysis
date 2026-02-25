import { innerAPI } from "@/api/api";
import type { Objects } from "@/store/";
import type { ObjectCreate } from "@/types";
import { Polygon, Polyline } from "leaflet";

export default class ObjectController {
  createObject = async (Obj: Objects) => {
    try {
      let newObject: ObjectCreate | null = null;

      if (Obj instanceof Polygon || Obj instanceof Polyline) {
        newObject = {
          latlng: Obj.getLatLngs().flat().flat(),
          options: Obj.options,
        };
      } else {
        const latlng = Obj.getLatLng();
        newObject = {
          latlng: [{ lat: latlng.lat, lng: latlng.lng }],
          options: Obj.options,
        };
      }
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
  };

  getObject = async (Id: string) => {
    try {
      if (innerAPI.objects) {
        const response = await innerAPI.objects.get_object(Id);
        if (response.status === "success") {
          return response;
        } else {
          console.error("error getting object", response);
          return response;
        }
      }
      throw new Error("pywebview is not registered");
    } catch (err) {
      console.error("bridge error:", err);
      throw err;
    }
  };

  getAllObjects = async () => {
    try {
      if (innerAPI.objects) {
        const response = await innerAPI.objects.get_all_objects();
        if (response.status === "success") {
          return response.objects;
        } else {
          console.error("error getting all objects", response);
          return null;
        }
      }
      throw new Error("pywebview is not registered");
    } catch (err) {
      console.error("bridge error:", err);
      throw err;
    }
  };

  deleteObject = async (Id: string) => {
    try {
      if (innerAPI.objects) {
        return await innerAPI.objects.delete_object(Id);
      }
      throw new Error("pywebview is not registered");
    } catch (err) {
      console.error("bridge error:", err);
      throw err;
    }
  };

  updateObject = async (Obj: Objects) => {
    try {
      let newObject: ObjectCreate | null = null;

      if (Obj instanceof Polygon || Obj instanceof Polyline) {
        newObject = {
          latlng: Obj.getLatLngs().flat().flat(),
          options: Obj.options,
        };
      } else {
        const latlng = Obj.getLatLng();
        newObject = {
          latlng: [{ lat: latlng.lat, lng: latlng.lng }],
          options: Obj.options,
        };
      }

      if (innerAPI.objects) {
        const response = await innerAPI.objects.update_object(newObject);
        if (response.status === "success") {
          return response;
        } else {
          console.error("error getting all objects", response);
          return null;
        }
      }
      throw new Error("pywebview is not registered");
    } catch (err) {
      console.error("bridge error:", err);
      throw err;
    }
  };
}
