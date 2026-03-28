import os
import sys
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker
from .object import Objects
from .tile_layer import TileLayers
from ..models import Base


class Storage:

    __instance = None
    localSession = None
    objects = None
    tile_layers = None

    def __init__(self):
        raise Exception("use the create method to create a storage")

    @classmethod
    def create(cls, engine: Engine):
        if cls.__instance is None:
            cls.__instance = cls.__new__(cls)
            cls.localSession = sessionmaker(
                autocommit=False, autoflush=False, bind=engine
            )
            cls.__init_db(engine)
            cls.objects = Objects(cls.localSession)
            cls.tile_layers = TileLayers(cls.localSession)
        return cls.__instance

    @staticmethod
    def get_base_dir():
        """Определяет корень, где лежит .exe или main.py"""
        if getattr(sys, "frozen", False) or "__compiled__" in globals():
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(sys.argv[0]))

    # Формируем путь к файлу БД

    @staticmethod
    def __init_db(engine: Engine):
        """Создает таблицы, если их еще нет"""
        Base.metadata.create_all(bind=engine)
