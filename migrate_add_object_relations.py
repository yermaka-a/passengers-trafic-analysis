"""
Миграция: Связи между объектами

Новая таблица: object_relations
- parent_id: полигон/полилайн (владелец)
- child_id: маркер (принадлежит)
- relation_type: тип связи (CONTAINS, BELONGS_TO)

Используется для:
- Хранения принадлежности маркеров полигонам/полилиниям
- Быстрого поиска всех маркеров в полигоне
- Скрытия маркеров вместе с полигоном
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "passengers.db"


def migrate():
    """Выполнить миграцию"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("📊 Миграция: object_relations...")

    # Проверка: существует ли уже таблица
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='object_relations'
    """)
    if cursor.fetchone():
        print("   ✅ Таблица object_relations уже существует")
        conn.close()
        return

    # Создаём таблицу object_relations
    print("   📐 Создание таблицы object_relations...")
    cursor.execute("""
        CREATE TABLE object_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id BLOB NOT NULL,
            child_id BLOB NOT NULL,
            relation_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (parent_id) REFERENCES map_objects(id) ON DELETE CASCADE,
            FOREIGN KEY (child_id) REFERENCES map_objects(id) ON DELETE CASCADE,
            
            UNIQUE(parent_id, child_id)
        )
    """)

    # Индексы для производительности
    print("   📈 Создание индексов...")
    cursor.execute("CREATE INDEX ix_relations_parent ON object_relations(parent_id)")
    cursor.execute("CREATE INDEX ix_relations_child ON object_relations(child_id)")
    cursor.execute("CREATE INDEX ix_relations_type ON object_relations(relation_type)")

    conn.commit()
    conn.close()

    print("   ✅ Миграция завершена успешно")


if __name__ == "__main__":
    migrate()
