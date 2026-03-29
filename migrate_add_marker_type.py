"""
Миграция: добавить колонку marker_type в таблицу map_objects
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "passengers.db"

def add_marker_type_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем есть ли колонка
    cursor.execute("PRAGMA table_info(map_objects)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "marker_type" in columns:
        print("✅ Колонка marker_type уже существует")
    else:
        print("➕ Добавляем колонку marker_type...")
        cursor.execute("""
            ALTER TABLE map_objects 
            ADD COLUMN marker_type VARCHAR(50) DEFAULT NULL
        """)
        conn.commit()
        print("✅ Колонка marker_type добавлена")
    
    conn.close()

if __name__ == "__main__":
    add_marker_type_column()
