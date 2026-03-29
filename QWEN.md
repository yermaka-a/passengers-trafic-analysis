# Проект: Passenger Traffic Analysis

## 📋 Обзор проекта

Приложение для визуального анализа пассажиропотока на карте. Позволяет создавать, редактировать и сохранять гео-объекты (полигоны, полилинии, круговые маркеры, маркеры остановок) с последующим хранением в SQLite базе данных.

## 🏗️ Архитектура

### Стек технологий

**Frontend:**
- Vue 3 + Vite + TypeScript
- MapLibre GL JS (карта)
- Deck.gl (визуализация гео-объектов: IconLayer, ScatterplotLayer, PolygonLayer, PathLayer)
- Pinia (state management)
- Tailwind CSS + shadcn-vue (UI компоненты)
- VueUse (composables утилиты)

**Backend:**
- Python 3.12+
- pywebview>=6.1 (гибридное desktop приложение)
- SQLAlchemy>=2.0.46 (ORM)
- Pydantic>=2.12.5 (валидация данных)
- Structlog>=25.5.0 (логирование)

### Структура проекта

```
first/
├── main.py                 # Точка входа Python приложения
├── pyproject.toml          # Python зависимости (uv/pip)
├── app/
│   ├── backend/            # Python backend
│   │   ├── app.py         # Инициализация pywebview окна
│   │   ├── api.py         # API контроллер
│   │   ├── crud/          # Бизнес-логика (ObjectController, LogsController, TileLayerController)
│   │   ├── models/        # SQLAlchemy модели (MapObject, TileLayerSetting)
│   │   ├── schemas/       # Pydantic схемы валидации
│   │   ├── storage/       # Storage класс (работа с БД)
│   │   ├── config/        # Конфигурация
│   │   └── logger/        # Настройки логирования
│   └── frontend/           # Vue 3 приложение
│       ├── src/
│       │   ├── components/ # Vue компоненты (Map, List, BrushTable, ObjectList)
│       │   ├── store/      # Pinia store (useMapObjectStore, useTilesStore)
│       │   ├── composables/# Композаблы (useApi, useDeckGL, useObjectActions)
│       │   ├── types/      # TypeScript типы (DeckGLObject, BackendObjectCreate)
│       │   ├── utils/      # Утилиты (конвертация координат, цветов)
│       │   ├── config/     # Конфигурация (DeckGLMapConfig, MaplibreMapConfig, stopMarkers.ts)
│       │   ├── api/        # API клиенты
│       │   └── assets/     # Статические файлы (cursor SVG)
│       ├── package.json    # Frontend зависимости
│       └── vite.config.ts  # Vite конфигурация
└── passengers.db           # SQLite база данных (создаётся автоматически)
```

## 🚀 Команды запуска

### Разработка

```bash
# Только frontend (Vite dev server, порт 5173)
yarn dev

# Backend + frontend через pywebview (основной режим)
python main.py

# Frontend + backend одновременно (backend пытается открыть pywebview окно)
yarn dev:all
```

### Сборка

```bash
# Сборка frontend в production
yarn build

# Запуск production версии (после сборки)
python main.py
```

## 🔧 Важные заметки

### Режимы работы

| Режим | Команда | Сохранение в БД | Примечание |
|-------|---------|-----------------|------------|
| **Frontend only** | `yarn dev` | ❌ НЕ работает | Объекты хранятся только в memory store |
| **Full app** | `python main.py` | ✅ Работает | Frontend внутри pywebview окна |
| **Dev all** | `yarn dev:all` | ⚠️ Через pywebview | Backend открывается в отдельном окне |

### API доступность

- **Доступно только через** `window.pywebview.api` когда приложение запущено через pywebview
- Ошибка `pywebview is not registered` означает, что frontend запущен в браузере, а не внутри pywebview
- После перезагрузки страницы при `yarn dev` все созданные объекты пропадут (не сохранены в БД)

## 🗺️ Карта и визуализация

### Слои Deck.gl

**Слои:**
- `PolygonLayer` — заливка полигонов
- `PathLayer` — контуры полигонов и полилинии
- `ScatterplotLayer` — круговые маркеры (CircleMarker)
- `IconLayer` — иконки остановок (StopMarker) с Lucide иконками

**Формат координат:**
- Backend: `[{lat, lng}, ...]`
- Deck.gl: `[[lng, lat], ...]` (GeoJSON standard)

**Конвертация:**
- `backendCoordsToDeckGL()` — из backend в Deck.gl
- `deckGLToBackendCoords()` — из Deck.gl в backend

**Цвета:**
- Backend: hex `#RRGGBB`
- Deck.gl: RGBA массив `[r, g, b, a]` (0-255)
- Конвертеры: `hexToRGBA()`, `rgbaToHex()`

### Типы маркеров

| Тип | Описание | Свойства |
|-----|----------|----------|
| **CircleMarker** | Круглый маркер | `radius`, `color`, `strokeWidth`, `strokeDasharray`, `fill`, `fillOpacity` |
| **StopMarker** | Иконка остановки (Lucide) | `radius` → `getSizeScale`, `markerType` (bus/train/tram/taxi/car/bike/default), `color` |

**StopMarker иконки:**
- Используются Lucide Icons из `lucide-vue-next`
- Sprite atlas генерируется через `generateIconAtlas()` в `config/stopMarkers.ts`
- 7 типов: bus, train, tram, taxi, car, bike, default
- Размер: `getSizeScale = radius / 30` (0.5 - 3.0)

## 🗄️ База данных

### Таблицы

**map_objects:**
- `Id` (VARCHAR(36), primary key)
- `name`, `description`, `custom_name`
- `color`, `stroke`, `weight`, `fill`, `fill_opacity`
- `latlng` (JSON), `obj_type`, `dash_array`
- `marker_type` (для StopMarker), `radius` (для StopMarker/CircleMarker)

**tile_layer_settings:**
- `id` (INTEGER, primary key)
- `key`, `value` (для сохранения текущего слоя карты)

### Миграции

```bash
# Добавить колонку marker_type
python migrate_add_marker_type.py

# Добавить колонку radius
python migrate_add_radius.py
```

## 🎨 UI Компоненты

### Основные компоненты
- **Map.vue** — карта с MapLibre + Deck.gl overlay
- **List.vue** — список объектов с настройками стилей (cards/table view)
- **BrushTable.vue** — выбор типа объекта (Polygon, Polyline, CircleMarker, StopMarker)
- **MapOptions.vue** — кнопки управления (добавить, отменить, undo/redo)
- **TilesSwitcher** — переключатель слоёв карты (OSM, Satellite, Hybrid, OpenFreeMap)

### Курсоры
- `plus-cursor.svg` — крест для режима рисования
- `grab-cursor.svg` — рука для перетаскивания
- Применяются через CSS с `!important` к `.maplibre-gl-canvas`

## 📦 Зависимости

### Python (pyproject.toml)
- `pywebview>=6.1` — desktop обёртка
- `sqlalchemy>=2.0.46` — ORM
- `pydantic>=2.12.5` — валидация
- `structlog>=25.5.0` — логирование
- `colorama>=0.4.6` — цвета в консоли

### Frontend (package.json)
- `@deck.gl/*@9.2.11` — визуализация (IconLayer, ScatterplotLayer, PolygonLayer, PathLayer)
- `maplibre-gl@3.6.2` — карта
- `vue@3.5.24` — фреймворк
- `pinia@3.0.4` — state management
- `shadcn-vue@2.4.3` — UI компоненты
- `lucide-vue-next@0.563.0` — иконки для StopMarker

## 🔧 Разработка

### Добавление нового слоя Deck.gl

1. Создать слой в `Map.vue`:
```typescript
new IconLayer({
  id: "my-layer",
  data: objects,
  getIcon: (obj) => obj.iconData?.svg,
  getPosition: (obj) => obj.coordinates[0],
  getSize: 24,
  getSizeScale: (obj) => obj.style.getSizeScale || 1.5,
  pickable: true,
})
```

2. Добавить в `createDeckLayers()` массив слоёв

3. Настроить стили в `DeckGLMapConfig.ts`

### Конвертация координат

```typescript
// Из backend в Deck.gl
const deckCoords = backendCoordsToDeckGL([{lat: 50, lng: 30}])
// Результат: [[30, 50]]

// Из Deck.gl в backend
const backendCoords = deckGLToBackendCoords([[30, 50]])
// Результат: [{lat: 50, lng: 30}]
```

## 📝 Git Workflow

### Ветки
- `develop` — основная ветка разработки
- `feat/*` — новые функции
- `fix/*` — исправления багов

### Коммиты
Следовать conventional commits:
- `feat:` новая функциональность
- `fix:` исправление бага
- `refactor:` рефакторинг
- `docs:` документация

## 🔗 Полезные ссылки

- [Deck.gl Documentation](https://deck.gl/docs)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js-docs/)
- [Vue 3 Guide](https://vuejs.org/guide/introduction.html)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [pywebview Docs](https://pywebview.flowrl.com/)
- [Lucide Icons](https://lucide.dev/icons/)
- [shadcn-vue](https://shadcn-vue.com/)
