import "leaflet";
import { ObjTypes } from "@/store";
declare module "leaflet" {
  interface PolylineOptions {
    Id: string;
    name: ObjNames;
    objType: Exclude<ObjTypes, "Edit">;
    CustomName?: string;
    description?: string;
  }
  interface CircleMarkerOptions {
    Id: string;
    name: ObjNames;
    objType: Exclude<ObjTypes, "Edit">;
    CustomName?: string;
    description?: string;
  }
}
import * as L from "leaflet";
export interface ObjectCreate {
  latlng: LatLng[];
  options: L.PolylineOptions | L.CircleMarkerOptions;
}
