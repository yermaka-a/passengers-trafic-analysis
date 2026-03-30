"""
Миграция: Пассажиропотоки (переработанная версия)

Пассажиропоток - это маршрут движения с остановками и количеством пассажиров

Новые таблицы:
1. passenger_flows - базовая информация о потоке
2. passenger_flow_stops - остановки в потоке с данными о пассажирах

Удаление старой таблицы passenger_flow (почасовой учёт)
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "passengers.db"


def migrate():
    """Выполнить миграцию"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("📊 Миграция: passenger_flows (переработка)...")

    # 1. Удаляем старую таблицу passenger_flow (почасовой учёт)
    print("   🗑️  Удаление старой таблицы passenger_flow...")
    cursor.execute("DROP TABLE IF EXISTS passenger_flow")

    # 2. Создаём новую таблицу passenger_flows
    print("   📐 Создание таблицы passenger_flows...")
    cursor.execute("""
        CREATE TABLE passenger_flows (
            id BLOB PRIMARY KEY,
            name TEXT NOT NULL,
            route_id BLOB,
            direction TEXT NOT NULL DEFAULT 'forward',
            date DATE NOT NULL,
            time_period TEXT NOT NULL DEFAULT 'off_peak',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE SET NULL
        )
    """)

    # 3. Создаём таблицу passenger_flow_stops
    print("   📐 Создание таблицы passenger_flow_stops...")
    cursor.execute("""
        CREATE TABLE passenger_flow_stops (
            flow_id BLOB NOT NULL,
            stop_id BLOB NOT NULL,
            stop_order INTEGER NOT NULL,
            passengers_on_board INTEGER DEFAULT 0,
            passengers_off_board INTEGER DEFAULT 0,
            passengers_remaining INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            PRIMARY KEY (flow_id, stop_order),
            FOREIGN KEY (flow_id) REFERENCES passenger_flows(id) ON DELETE CASCADE,
            FOREIGN KEY (stop_id) REFERENCES map_objects(id) ON DELETE CASCADE
        )
    """)

    # Индексы для производительности
    print("   📈 Создание индексов...")
    cursor.execute("CREATE INDEX ix_pf_date ON passenger_flows(date)")
    cursor.execute("CREATE INDEX ix_pf_direction ON passenger_flows(direction)")
    cursor.execute("CREATE INDEX ix_pf_time_period ON passenger_flows(time_period)")
    cursor.execute("CREATE INDEX ix_pfs_flow ON passenger_flow_stops(flow_id)")
    cursor.execute("CREATE INDEX ix_pfs_stop ON passenger_flow_stops(stop_id)")

    conn.commit()
    conn.close()

    print("   ✅ Миграция завершена успешно")


if __name__ == "__main__":
    migrate()
