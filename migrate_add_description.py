"""
Миграция: добавить поле description в map_objects
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "passengers.db"


def migrate():
    """Выполнить миграцию"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("📊 Начало миграции: добавление поля description...")
    
    # Добавляем поле description если его нет
    try:
        cursor.execute("ALTER TABLE map_objects ADD COLUMN description TEXT")
        print("✅ Поле description добавлено")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("⚠️  Поле description уже существует")
        else:
            raise
    
    conn.commit()
    conn.close()
    print("✅ Миграция завершена успешно!")


if __name__ == "__main__":
    migrate()
