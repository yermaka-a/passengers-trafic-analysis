"""
Миграция: Пассажиропоток остановок

Новая таблица: passenger_flow
- stop_id: ссылка на StopMarker
- date: дата записи
- hour: час (0-23)
- incoming: входящие пассажиры
- outgoing: исходящие пассажиры

Используется для:
- Учёта пассажиропотока по часам
- Агрегации данных по полигонам/маршрутам
- Построения отчётов и аналитики
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "passengers.db"


def migrate():
    """Выполнить миграцию"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("📊 Миграция: passenger_flow...")

    # Проверка: существует ли уже таблица
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='passenger_flow'
    """)
    if cursor.fetchone():
        print("   ✅ Таблица passenger_flow уже существует")
        conn.close()
        return

    # Создаём таблицу passenger_flow
    print("   📐 Создание таблицы passenger_flow...")
    cursor.execute("""
        CREATE TABLE passenger_flow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stop_id BLOB NOT NULL,
            date DATE NOT NULL,
            hour INTEGER NOT NULL CHECK(hour >= 0 AND hour <= 23),
            incoming INTEGER DEFAULT 0,
            outgoing INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (stop_id) REFERENCES map_objects(id) ON DELETE CASCADE,
            
            UNIQUE(stop_id, date, hour)
        )
    """)

    # Индексы для производительности
    print("   📈 Создание индексов...")
    cursor.execute("CREATE INDEX ix_flow_stop ON passenger_flow(stop_id)")
    cursor.execute("CREATE INDEX ix_flow_date ON passenger_flow(date)")
    cursor.execute("CREATE INDEX ix_flow_stop_date ON passenger_flow(stop_id, date)")

    conn.commit()
    conn.close()

    print("   ✅ Миграция завершена успешно")


if __name__ == "__main__":
    migrate()
