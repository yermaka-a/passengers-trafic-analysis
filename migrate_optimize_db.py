"""
Миграция: оптимизация БД
- Добавление индексов для производительности
- Добавление полей latitude/longitude для быстрого поиска по координатам
"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "passengers.db"


def migrate():
    """Выполнить миграцию"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("📊 Начало миграции...")
    
    # 1. Добавить поля latitude/longitude если их нет
    print("➕ Добавление полей latitude/longitude...")
    try:
        cursor.execute("ALTER TABLE map_objects ADD COLUMN latitude FLOAT")
        cursor.execute("ALTER TABLE map_objects ADD COLUMN longitude FLOAT")
        print("✅ Поля добавлены")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("⚠️  Поля уже существуют")
        else:
            raise
    
    # 2. Заполнить latitude/longitude из JSON latlng
    print("📍 Заполнение latitude/longitude из JSON...")
    cursor.execute("""
    UPDATE map_objects 
    SET 
        latitude = json_extract(latlng, '$[0].lat'),
        longitude = json_extract(latlng, '$[0].lng')
    WHERE json_valid(latlng) AND latlng IS NOT NULL
    """)
    updated = cursor.rowcount
    print(f"✅ Обновлено {updated} записей")
    
    # 3. Создать индексы
    print("📑 Создание индексов...")
    indexes = [
        ("ix_obj_type", "CREATE INDEX IF NOT EXISTS ix_obj_type ON map_objects(obj_type)"),
        ("ix_marker_type", "CREATE INDEX IF NOT EXISTS ix_marker_type ON map_objects(marker_type)"),
        ("ix_obj_type_marker", "CREATE INDEX IF NOT EXISTS ix_obj_type_marker ON map_objects(obj_type, marker_type)"),
        ("ix_custom_name", "CREATE INDEX IF NOT EXISTS ix_custom_name ON map_objects(custom_name)"),
        ("ix_name", "CREATE INDEX IF NOT EXISTS ix_name ON map_objects(name)"),
        ("ix_latitude", "CREATE INDEX IF NOT EXISTS ix_latitude ON map_objects(latitude)"),
        ("ix_longitude", "CREATE INDEX IF NOT EXISTS ix_longitude ON map_objects(longitude)"),
    ]
    
    for idx_name, idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
            print(f"✅ Индекс {idx_name} создан")
        except sqlite3.OperationalError as e:
            if "already exists" in str(e).lower():
                print(f"⚠️  Индекс {idx_name} уже существует")
            else:
                raise
    
    conn.commit()
    
    # 4. Показать статистику
    print("\n📊 Статистика:")
    cursor.execute("SELECT COUNT(*) FROM map_objects")
    total = cursor.fetchone()[0]
    print(f"   Всего объектов: {total}")
    
    cursor.execute("SELECT COUNT(*) FROM map_objects WHERE obj_type = 'StopMarker'")
    stops = cursor.fetchone()[0]
    print(f"   Остановок (StopMarker): {stops}")
    
    cursor.execute("SELECT COUNT(*) FROM map_objects WHERE latitude IS NOT NULL")
    with_coords = cursor.fetchone()[0]
    print(f"   С координатами: {with_coords}")
    
    conn.close()
    print("\n✅ Миграция завершена успешно!")


if __name__ == "__main__":
    migrate()
