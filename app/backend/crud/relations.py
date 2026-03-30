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
from sqlalchemy.orm import Session, sessionmaker
import uuid

from ..models import ObjectRelation, MapObject
from ..logger import log


class ObjectRelationsController:
    def __init__(self, sessionmaker: sessionmaker):
        self.sessionmaker = sessionmaker

    def _get_session(self) -> Session:
        return self.sessionmaker()

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
                # Проверяем существование объектов
                parent = session.get(MapObject, uuid.UUID(parent_id).bytes)
                child = session.get(MapObject, uuid.UUID(child_id).bytes)
                
                if not parent or not child:
                    log.warning("add_relation: объект не найден", extra={
                        "parent_id": parent_id,
                        "child_id": child_id
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
            log.error("add_relation: ошибка", extra={"error": str(e)})
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
                relations = session.execute(
                    select(ObjectRelation).where(
                        ObjectRelation.parent_id == uuid.UUID(parent_id).bytes
                    )
                ).scalars().all()
                
                children = []
                for relation in relations:
                    child = session.get(MapObject, relation.child_id)
                    if child:
                        children.append(child)
                
                log.info("get_children: найдено объектов", extra={
                    "parent_id": parent_id,
                    "count": len(children)
                })
                return children
                
        except Exception as e:
            log.error("get_children: ошибка", extra={"error": str(e)})
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
