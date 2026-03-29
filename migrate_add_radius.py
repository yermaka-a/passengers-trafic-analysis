"""
Миграция: добавить колонку radius в таблицу map_objects
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "passengers.db"

def add_radius_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем есть ли колонка
    cursor.execute("PRAGMA table_info(map_objects)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "radius" in columns:
        print("✅ Колонка radius уже существует")
    else:
        print("➕ Добавляем колонку radius...")
        cursor.execute("""
            ALTER TABLE map_objects 
            ADD COLUMN radius INTEGER DEFAULT 30
        """)
        conn.commit()
        print("✅ Колонка radius добавлена")
    
    conn.close()

if __name__ == "__main__":
    add_radius_column()
