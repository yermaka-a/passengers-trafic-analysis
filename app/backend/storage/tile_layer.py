from ..models.tile_layer import TileLayerSetting
from sqlalchemy.orm import Session


class TileLayers:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get(self, key: str) -> str | None:
        try:
            with self.session_factory() as session:
                setting = session.query(TileLayerSetting).filter_by(key=key).first()
                print(f'[TileLayers] get({key}) = {setting.value if setting else None}')
                return setting.value if setting else None
        except Exception as e:
            print(f'[TileLayers] get error: {e}')
            return None

    def set(self, key: str, value: str):
        try:
            with self.session_factory() as session:
                setting = session.query(TileLayerSetting).filter_by(key=key).first()
                if setting:
                    setting.value = value
                    print(f'[TileLayers] set({key}) = {value} (updated)')
                else:
                    new_setting = TileLayerSetting(key=key, value=value)
                    session.add(new_setting)
                    print(f'[TileLayers] set({key}) = {value} (created)')
                session.commit()
        except Exception as e:
            print(f'[TileLayers] set error: {e}')
            session.rollback()
