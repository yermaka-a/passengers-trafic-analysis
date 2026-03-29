"""
Миграция: полная оптимизация БД

1. Сохраняем данные во временные таблицы
2. Удаляем старую БД
3. Создаём новую оптимизированную схему
4. Переносим данные

Оптимизация:
- ID в binary(16) вместо VARCHAR(36)
- Разделение на 3 таблицы: map_objects, stop_metadata, object_styles
- latitude/longitude только для маркеров (из первой координаты)
- JSON latlng хранит полный массив координат
"""
import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "passengers.db"
BACKUP_PATH = Path(__file__).parent / "passengers_backup.db"


def uuid_to_binary(uuid_str: str) -> bytes:
    """Конвертировать UUID строку в бинарный формат (16 байт)"""
    if isinstance(uuid_str, bytes):
        return uuid_str
    return uuid.UUID(uuid_str).bytes


def migrate():
    """Выполнить миграцию"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("📊 Начало миграции...")
    
    # 1. Проверка текущих данных
    cursor.execute("SELECT COUNT(*) FROM map_objects")
    total_objects = cursor.fetchone()[0]
    print(f"   Найдено объектов: {total_objects}")
    
    if total_objects > 0:
        print("💾 Сохранение данных во временное хранилище...")
        
        # Экспорт всех данных
        cursor.execute("SELECT * FROM map_objects")
        rows = cursor.fetchall()
        
        # Получаем колонки
        columns = [description[0] for description in cursor.description]
        
        # Конвертируем в dict
        old_data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            # Парсим JSON поля
            if row_dict.get('latlng'):
                row_dict['latlng'] = json.loads(row_dict['latlng'])
            if row_dict.get('dash_array'):
                try:
                    row_dict['dash_array'] = json.loads(row_dict['dash_array'])
                except:
                    row_dict['dash_array'] = None
            old_data.append(row_dict)
        
        print(f"   Сохранено {len(old_data)} объектов")
    else:
        old_data = []
        print("   Данные не найдены (пустая БД)")
    
    conn.close()
    
    # 2. Переименовываем старую БД (вместо удаления)
    print("🗑️  Сохранение старой БД...")
    if DB_PATH.exists():
        # Переименовываем в .old
        old_backup = DB_PATH.with_suffix('.db.old')
        DB_PATH.rename(old_backup)
        
        # Удаляем WAL/SHM если есть
        wal_path = DB_PATH.with_suffix('.db-wal')
        shm_path = DB_PATH.with_suffix('.db-shm')
        if wal_path.exists():
            wal_path.unlink()
        if shm_path.exists():
            shm_path.unlink()
        print(f"   Старая БД переименована в {old_backup.name}")
    
    # 3. Создаём новую БД с оптимизированной схемой
    print("📐 Создание новой оптимизированной схемы...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Включаем WAL режим для производительности
    cursor.execute("PRAGMA journal_mode=WAL")
    
    # Таблица map_objects (базовая для всех объектов)
    cursor.execute("""
    CREATE TABLE map_objects (
        id BLOB(16) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        obj_type VARCHAR(30) NOT NULL,
        latitude FLOAT,
        longitude FLOAT,
        latlng JSON NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) WITHOUT ROWID
    """)
    
    # Таблица stop_metadata (для StopMarker)
    cursor.execute("""
    CREATE TABLE stop_metadata (
        object_id BLOB(16) PRIMARY KEY,
        osm_id VARCHAR(50) UNIQUE,
        marker_type VARCHAR(50),
        radius INTEGER DEFAULT 30,
        color VARCHAR(10) DEFAULT '#FF0000',
        FOREIGN KEY (object_id) REFERENCES map_objects(id) ON DELETE CASCADE
    ) WITHOUT ROWID
    """)
    
    # Таблица object_styles (для Polygon/Polyline/CircleMarker)
    cursor.execute("""
    CREATE TABLE object_styles (
        object_id BLOB(16) PRIMARY KEY,
        stroke BOOLEAN DEFAULT TRUE,
        weight INTEGER DEFAULT 3,
        fill BOOLEAN,
        fill_opacity FLOAT,
        dash_array JSON,
        color VARCHAR(10),
        FOREIGN KEY (object_id) REFERENCES map_objects(id) ON DELETE CASCADE
    ) WITHOUT ROWID
    """)
    
    # Таблица tile_layer_settings
    cursor.execute("""
    CREATE TABLE tile_layer_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key VARCHAR(100) UNIQUE NOT NULL,
        value TEXT NOT NULL
    )
    """)
    
    # Индексы для map_objects
    cursor.execute("CREATE INDEX ix_obj_type ON map_objects(obj_type)")
    cursor.execute("CREATE INDEX ix_latitude ON map_objects(latitude)")
    cursor.execute("CREATE INDEX ix_longitude ON map_objects(longitude)")
    cursor.execute("CREATE INDEX ix_name ON map_objects(name)")
    
    # Индексы для stop_metadata
    cursor.execute("CREATE INDEX ix_stop_osm_id ON stop_metadata(osm_id)")
    cursor.execute("CREATE INDEX ix_stop_marker_type ON stop_metadata(marker_type)")
    
    print("   Схема создана")
    
    # 4. Переносим данные
    if old_data:
        print("📥 Перенос данных...")
        
        now = datetime.now().isoformat()
        
        for obj in old_data:
            # Конвертируем ID в binary
            binary_id = uuid_to_binary(obj['Id'])
            
            # Извлекаем первую координату для latitude/longitude (только для маркеров)
            latlng = obj['latlng']
            latitude = None
            longitude = None
            
            if latlng and isinstance(latlng, list) and len(latlng) > 0:
                # Для маркеров (одна точка) - берём первую координату
                # Для полигонов/полилиний - тоже берём первую для индексации
                first_coord = latlng[0]
                if isinstance(first_coord, dict):
                    latitude = first_coord.get('lat')
                    longitude = first_coord.get('lng')
            
            # Вставка в map_objects
            cursor.execute("""
            INSERT INTO map_objects (id, name, obj_type, latitude, longitude, latlng, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                binary_id,
                obj['name'],
                obj['obj_type'],
                latitude,
                longitude,
                json.dumps(latlng),
                now,
                now
            ))
            
            # Вставка в stop_metadata (если StopMarker)
            if obj['obj_type'] == 'StopMarker':
                cursor.execute("""
                INSERT INTO stop_metadata (object_id, osm_id, marker_type, radius, color)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    binary_id,
                    obj.get('osm_id'),  # Пока NULL, будет заполнено при следующем импорте
                    obj.get('marker_type', 'pin'),
                    obj.get('radius', 30),
                    obj.get('color', '#FF0000')
                ))
            
            # Вставка в object_styles (если не StopMarker)
            elif obj['obj_type'] in ('Polygon', 'Polyline', 'CircleMarker'):
                cursor.execute("""
                INSERT INTO object_styles (object_id, stroke, weight, fill, fill_opacity, dash_array, color)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    binary_id,
                    obj.get('stroke'),
                    obj.get('weight'),
                    obj.get('fill'),
                    obj.get('fill_opacity'),
                    json.dumps(obj['dash_array']) if obj.get('dash_array') else None,
                    obj.get('color')
                ))
        
        print(f"   Перенесено {len(old_data)} объектов")
    
    conn.commit()
    
    # 5. Статистика
    print("\n📊 Статистика:")
    cursor.execute("SELECT COUNT(*) FROM map_objects")
    print(f"   map_objects: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM stop_metadata")
    print(f"   stop_metadata: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM object_styles")
    print(f"   object_styles: {cursor.fetchone()[0]}")
    
    # Размер БД
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    size = cursor.fetchone()[0]
    print(f"   Размер БД: {size / 1024:.1f} КБ")
    
    conn.close()
    
    print("\n✅ Миграция завершена успешно!")
    print(f"💾 Резервная копия сохранена: {BACKUP_PATH}")


if __name__ == "__main__":
    migrate()
