"""
Миграция: Маршруты

Новые таблицы:
1. routes - базовая информация о маршрутах
2. route_stops - остановки в маршруте (порядковый список)

Используется для:
- Хранения маршрутов транспорта
- Порядка следования остановок
- Направления движения (forward/backward)
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "passengers.db"


def migrate():
    """Выполнить миграцию"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("📊 Миграция: routes...")

    # Проверка: существует ли уже таблица routes
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='routes'
    """)
    if cursor.fetchone():
        print("   ✅ Таблица routes уже существует")
        conn.close()
        return

    # Создаём таблицу routes
    print("   📐 Создание таблицы routes...")
    cursor.execute("""
        CREATE TABLE routes (
            id BLOB PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            direction TEXT DEFAULT 'forward' CHECK(direction IN ('forward', 'backward')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Создаём таблицу route_stops
    print("   📐 Создание таблицы route_stops...")
    cursor.execute("""
        CREATE TABLE route_stops (
            route_id BLOB NOT NULL,
            stop_id BLOB NOT NULL,
            stop_order INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            PRIMARY KEY (route_id, stop_order),
            FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE,
            FOREIGN KEY (stop_id) REFERENCES map_objects(id) ON DELETE CASCADE,
            
            UNIQUE(route_id, stop_id)
        )
    """)

    # Индексы для производительности
    print("   📈 Создание индексов...")
    cursor.execute("CREATE INDEX ix_routes_name ON routes(name)")
    cursor.execute("CREATE INDEX ix_route_stops_route ON route_stops(route_id)")
    cursor.execute("CREATE INDEX ix_route_stops_stop ON route_stops(stop_id)")

    conn.commit()
    conn.close()

    print("   ✅ Миграция завершена успешно")


if __name__ == "__main__":
    migrate()
