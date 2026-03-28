from ..models.tile_layer import TileLayerSetting
from ..schemas.tile_layer import TileLayerSettingCreate, TileLayerSettingResponse
from ..logger import log


class TileLayerController:
    def __init__(self, storage) -> None:
        if storage.tile_layers is None:
            raise Exception("storage.tile_layers not created")
        self.tile_layers = storage.tile_layers

    def get_current_layer(self):
        try:
            setting = self.tile_layers.get("current_layer")
            log.info("get_current_layer", extra={"layer": setting})
            return {"status": "success", "layer": setting or "osm"}
        except Exception as e:
            op = "get_current_layer"
            log.error(op, {"err": e})
            return {"status": "failed", "layer": "osm"}

    def set_current_layer(self, layer: str):
        try:
            self.tile_layers.set("current_layer", layer)
            log.info("set_current_layer", extra={"layer": layer})
            return {"status": "success", "layer": layer}
        except Exception as e:
            op = "set_current_layer"
            log.error(op, {"err": e})
            return {"status": "failed", "layer": layer}
