import { defineStore } from "pinia";

interface TilesState {
  OSM: { TilesURL: string; TilesName: string };
}

export const useTilesStore = defineStore("tiles", {
  state: (): TilesState => {
    return {
      OSM: {
        TilesURL: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        TilesName: "openstreetmap",
      },
    };
  },
});
