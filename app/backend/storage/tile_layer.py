from ..models.tile_layer import TileLayerSetting
from sqlalchemy.orm import Session


class TileLayers:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get(self, key: str) -> str | None:
        with self.session_factory() as session:
            setting = session.query(TileLayerSetting).filter_by(key=key).first()
            return setting.value if setting else None

    def set(self, key: str, value: str):
        with self.session_factory() as session:
            setting = session.query(TileLayerSetting).filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                new_setting = TileLayerSetting(key=key, value=value)
                session.add(new_setting)
            session.commit()
