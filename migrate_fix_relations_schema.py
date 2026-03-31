"""
Миграция: Изменить тип parent_id и child_id в object_relations с String(16) на String(36)

UUID хранится как строка с дефисами (36 символов), а не как binary (16 байт)
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "passengers.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем текущую схему
    cursor.execute("PRAGMA table_info(object_relations)")
    columns = cursor.fetchall()
    print("Текущая схема object_relations:")
    for col in columns:
        print(f"  {col[1]}: {col[2]}")
    
    # В SQLite нельзя изменить тип колонки напрямую, нужно пересоздать таблицу
    # Но для String(16) -> String(36) данные совместимы, просто увеличиваем размер
    
    # Создаём новую таблицу с правильными типами
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS object_relations_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id VARCHAR(36) NOT NULL,
            child_id VARCHAR(36) NOT NULL,
            relation_type VARCHAR(30) NOT NULL DEFAULT 'CONTAINS',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(parent_id, child_id)
        )
    """)
    
    # Копируем данные
    cursor.execute("""
        INSERT INTO object_relations_new (id, parent_id, child_id, relation_type, created_at)
        SELECT id, parent_id, child_id, relation_type, created_at
        FROM object_relations
    """)
    
    # Удаляем старую таблицу
    cursor.execute("DROP TABLE object_relations")
    
    # Переименовываем новую
    cursor.execute("ALTER TABLE object_relations_new RENAME TO object_relations")
    
    # Создаём индексы
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_relations_parent ON object_relations(parent_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_relations_child ON object_relations(child_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_relations_type ON object_relations(relation_type)")
    
    conn.commit()
    
    # Проверяем результат
    cursor.execute("PRAGMA table_info(object_relations)")
    columns = cursor.fetchall()
    print("\nНовая схема object_relations:")
    for col in columns:
        print(f"  {col[1]}: {col[2]}")
    
    # Проверяем данные
    cursor.execute("SELECT COUNT(*) FROM object_relations")
    count = cursor.fetchone()[0]
    print(f"\nПеренесено записей: {count}")
    
    # Показываем пример данных
    cursor.execute("SELECT parent_id, child_id FROM object_relations LIMIT 3")
    samples = cursor.fetchall()
    print("\nПример данных:")
    for s in samples:
        print(f"  parent_id={s[0]}, child_id={s[1]}")
    
    conn.close()
    print("\n✅ Миграция завершена успешно!")

if __name__ == "__main__":
    migrate()
