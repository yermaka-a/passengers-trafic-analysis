"""
CRUD операции для связей между объектами

ObjectRelations:
- add_relation(parent_id, child_id, relation_type)
- remove_relation(parent_id, child_id)
- get_children(parent_id) - получить все маркеры в полигоне/полилинии
- get_parents(child_id) - получить все полигоны/полилинии для маркера
- auto_assign_stops_to_polygons() - автоматическое назначение
"""
from typing import List, Optional
from sqlalchemy import select
import uuid

from ..models import ObjectRelation, MapObject
from ..models.object import binary_to_uuid
from ..logger import log


class ObjectRelationsController:
    def __init__(self, storage):
        self.storage = storage

    def _get_session(self):
        return self.storage.localSession()

    def add_relation(self, parent_id: str, child_id: str, relation_type: str = 'CONTAINS') -> bool:
        """
        Добавить связь между объектами
        
        Args:
            parent_id: UUID родителя (полигон/полилайн)
            child_id: UUID потомка (маркер)
            relation_type: тип связи ('CONTAINS', 'BELONGS_TO')
            
        Returns:
            True если успешно
        """
        try:
            with self._get_session() as session:
                # Конвертируем UUID строки в бинарный формат
                parent_uuid = uuid.UUID(parent_id)
                child_uuid = uuid.UUID(child_id)
                
                log.info("add_relation: поиск объектов", extra={
                    "parent_id": parent_id,
                    "child_id": child_id
                })
                
                # Получаем все объекты и ищем в памяти
                all_objects = session.execute(select(MapObject)).scalars().all()
                
                parent = None
                child = None
                
                for obj in all_objects:
                    obj_uuid = binary_to_uuid(obj.id)
                    if obj_uuid == parent_id:
                        parent = obj
                    if obj_uuid == child_id:
                        child = obj

                log.info("add_relation: результат поиска", extra={
                    "parent_found": parent is not None,
                    "child_found": child is not None
                })

                if not parent or not child:
                    log.warning("add_relation: объект не найден", extra={
                        "parent_id": parent_id,
                        "parent_found": parent is not None,
                        "child_id": child_id,
                        "child_found": child is not None
                    })
                    return False

                # Проверяем что связь ещё не существует
                existing = session.execute(
                    select(ObjectRelation).where(
                        ObjectRelation.parent_id == parent.id,
                        ObjectRelation.child_id == child.id
                    )
                ).scalar_one_or_none()

                if existing:
                    log.info("add_relation: связь уже существует", extra={
                        "parent_id": parent_id,
                        "child_id": child_id
                    })
                    return True

                # Создаём связь
                relation = ObjectRelation(
                    id=None,  # autoincrement
                    parent_id=parent.id,
                    child_id=child.id,
                    relation_type=relation_type
                )
                session.add(relation)
                session.commit()

                log.info("add_relation: связь добавлена", extra={
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "relation_type": relation_type
                })
                return True
                
        except Exception as e:
            log.error("add_relation: ошибка", extra={"error": str(e), "traceback": __import__('traceback').format_exc()})
            return False

    def remove_relation(self, parent_id: str, child_id: str) -> bool:
        """
        Удалить связь между объектами
        
        Args:
            parent_id: UUID родителя
            child_id: UUID потомка
            
        Returns:
            True если успешно
        """
        try:
            with self._get_session() as session:
                relation = session.execute(
                    select(ObjectRelation).where(
                        ObjectRelation.parent_id == uuid.UUID(parent_id).bytes,
                        ObjectRelation.child_id == uuid.UUID(child_id).bytes
                    )
                ).scalar_one_or_none()
                
                if relation:
                    session.delete(relation)
                    session.commit()
                    log.info("remove_relation: связь удалена", extra={
                        "parent_id": parent_id,
                        "child_id": child_id
                    })
                    return True
                else:
                    log.warning("remove_relation: связь не найдена", extra={
                        "parent_id": parent_id,
                        "child_id": child_id
                    })
                    return False
                    
        except Exception as e:
            log.error("remove_relation: ошибка", extra={"error": str(e)})
            return False

    def get_children(self, parent_id: str) -> List[MapObject]:
        """
        Получить все дочерние объекты (маркеры в полигоне/полилинии)

        Args:
            parent_id: UUID родителя

        Returns:
            Список MapObject
        """
        try:
            with self._get_session() as session:
                # Конвертируем UUID строку в bytes
                parent_uuid = uuid.UUID(parent_id)
                parent_id_bytes = parent_uuid.bytes
                parent_id_hex = parent_uuid.hex
                
                log.info("get_children: входные данные", extra={
                    "parent_id": parent_id,
                    "parent_id_bytes_len": len(parent_id_bytes),
                    "parent_id_hex": parent_id_hex
                })
                
                # Проверяем что есть в БД
                all_relations = session.execute(
                    text("SELECT parent_id, child_id, hex(parent_id) as parent_hex, hex(child_id) as child_hex FROM object_relations")
                ).fetchall()
                
                log.info("get_children: все связи в БД", extra={
                    "total_relations": len(all_relations),
                    "sample": [(r[2], r[3]) for r in all_relations[:5]]  # hex представления
                })
                
                # Ищем связи через raw SQL
                from sqlalchemy import text
                result = session.execute(
                    text("""
                        SELECT mo.id, mo.name, mo.obj_type, mo.latlng, mo.description,
                               mo.latitude, mo.longitude, mo.created_at, mo.updated_at
                        FROM map_objects mo
                        INNER JOIN object_relations orel ON mo.id = orel.child_id
                        WHERE hex(orel.parent_id) = :parent_id_hex
                    """),
                    {"parent_id_hex": parent_id_hex}
                )
                
                children = []
                for row in result:
                    child = MapObject(
                        id=row[0],
                        name=row[1],
                        obj_type=row[2],
                        latlng=row[3],
                        description=row[4],
                        latitude=row[5],
                        longitude=row[6],
                        created_at=row[7],
                        updated_at=row[8]
                    )
                    children.append(child)

                log.info("get_children: найдено объектов", extra={
                    "parent_id": parent_id,
                    "count": len(children)
                })
                return children

        except Exception as e:
            log.error("get_children: ошибка", extra={"error": str(e), "traceback": __import__('traceback').format_exc()})
            return []

    def get_parents(self, child_id: str) -> List[MapObject]:
        """
        Получить все родительские объекты (полигоны/полилинии для маркера)
        
        Args:
            child_id: UUID потомка
            
        Returns:
            Список MapObject
        """
        try:
            with self._get_session() as session:
                relations = session.execute(
                    select(ObjectRelation).where(
                        ObjectRelation.child_id == uuid.UUID(child_id).bytes
                    )
                ).scalars().all()
                
                parents = []
                for relation in relations:
                    parent = session.get(MapObject, relation.parent_id)
                    if parent:
                        parents.append(parent)
                
                log.info("get_parents: найдено объектов", extra={
                    "child_id": child_id,
                    "count": len(parents)
                })
                return parents
                
        except Exception as e:
            log.error("get_parents: ошибка", extra={"error": str(e)})
            return []

    def remove_all_relations_for_parent(self, parent_id: str) -> int:
        """
        Удалить все связи для родителя
        
        Args:
            parent_id: UUID родителя
            
        Returns:
            Количество удалённых связей
        """
        try:
            with self._get_session() as session:
                relations = session.execute(
                    select(ObjectRelation).where(
                        ObjectRelation.parent_id == uuid.UUID(parent_id).bytes
                    )
                ).scalars().all()
                
                count = len(relations)
                for relation in relations:
                    session.delete(relation)
                
                session.commit()
                log.info("remove_all_relations_for_parent: удалено связей", extra={
                    "parent_id": parent_id,
                    "count": count
                })
                return count
                
        except Exception as e:
            log.error("remove_all_relations_for_parent: ошибка", extra={"error": str(e)})
            return 0

    def remove_all_relations_for_child(self, child_id: str) -> int:
        """
        Удалить все связи для потомка
        
        Args:
            child_id: UUID потомка
            
        Returns:
            Количество удалённых связей
        """
        try:
            with self._get_session() as session:
                relations = session.execute(
                    select(ObjectRelation).where(
                        ObjectRelation.child_id == uuid.UUID(child_id).bytes
                    )
                ).scalars().all()
                
                count = len(relations)
                for relation in relations:
                    session.delete(relation)
                
                session.commit()
                log.info("remove_all_relations_for_child: удалено связей", extra={
                    "child_id": child_id,
                    "count": count
                })
                return count
                
        except Exception as e:
            log.error("remove_all_relations_for_child: ошибка", extra={"error": str(e)})
            return 0
