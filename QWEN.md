# Проект: Passenger Traffic Analysis

## 📋 Обзор проекта

Приложение для визуального анализа пассажиропотока на карте. Позволяет создавать, редактировать и сохранять гео-объекты (полигоны, полилинии, круговые маркеры) с последующим хранением в SQLite базе данных.

## 🏗️ Архитектура

### Стек технологий

**Frontend:**
- Vue 3 + Vite + TypeScript
- MapLibre GL JS (карта)
- Deck.gl (визуализация гео-объектов)
- Pinia (state management)
- Tailwind CSS + shadcn-vue (UI компоненты)
- VueUse (composables утилиты)

**Backend:**
- Python 3.12+
- pywebview (гибридное desktop приложение)
- SQLAlchemy (ORM)
- Pydantic (валидация данных)
- Structlog (логирование)

### Структура проекта

```
first/
├── main.py                 # Точка входа Python приложения
├── pyproject.toml          # Python зависимости (uv/pip)
├── app/
│   ├── backend/            # Python backend
│   │   ├── app.py         # Инициализация pywebview окна
│   │   ├── api.py         # API контроллер
│   │   ├── crud/          # Бизнес-логика (ObjectController, LogsController)
│   │   ├── models/        # SQLAlchemy модели
│   │   ├── schemas/       # Pydantic схемы валидации
│   │   ├── storage/       # Storage класс (работа с БД)
│   │   ├── config/        # Конфигурация
│   │   └── logger/        # Настройки логирования
│   └── frontend/           # Vue 3 приложение
│       ├── src/
│       │   ├── components/ # Vue компоненты (Map, List, BrushTable)
│       │   ├── store/      # Pinia store (useMapStore, useMapObjectStore)
│       │   ├── composables/# Композаблы (useApi, useL7)
│       │   ├── types/      # TypeScript типы
│       │   ├── utils/      # Утилиты (конвертация координат, цветов)
│       │   ├── config/     # Конфигурация (DeckGLMapConfig, MaplibreMapConfig)
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

### Текущая реализация (MapLibre + Deck.gl)

**Слои Deck.gl:**
- `PolygonLayer` — заливка полигонов
- `PathLayer` — контуры полигонов и полилинии
- `ScatterplotLayer` — круговые маркеры

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

### История миграции

Проект мигрировал с **Leaflet + Deck.gl** на **MapLibre GL JS + Deck.gl** для решения проблем с рендерингом WebGL.

**Проблема L7:** AntV L7 не создавал WebGL контекст корректно с MapLibre adapter.

**Решение:** Использован `MapboxOverlay` из `@deck.gl/mapbox` с `interleaved: true` для правильной интеграции с MapLibre.

## 📦 Зависимости

### Python (pyproject.toml)
- `pywebview>=6.1` — desktop обёртка
- `sqlalchemy>=2.0.46` — ORM
- `pydantic>=2.12.5` — валидация
- `structlog>=25.5.0` — логирование
- `colorama>=0.4.6` — цвета в консоли

### Frontend (package.json)
- `@deck.gl/*@9.2.11` — визуализация
- `maplibre-gl@3.6.2` — карта
- `vue@3.5.24` — фреймворк
- `pinia@3.0.4` — state management
- `shadcn-vue@2.4.3` — UI компоненты
- `@turf/turf@7.3.3` — гео-утилиты

## 🎨 UI Компоненты

### Основные компоненты
- **Map.vue** — карта с MapLibre + Deck.gl overlay
- **List.vue** — список объектов с настройками стилей
- **BrushTable.vue** — выбор типа объекта (Polygon, Polyline, CircleMarker)
- **MapOptions.vue** — кнопки управления (добавить, отменить, undo/redo)
- **TilesSwitcher.vue** — переключение слоёв карты (OSM, Satellite, Hybrid)

### Курсоры
- `plus-cursor.svg` — крест для режима рисования
- `grab-cursor.svg` — рука для перетаскивания
- Применяются через CSS с `!important` к `.maplibregl-canvas`

## 🧪 Тестирование

### Ручное тестирование

1. **Создание полигона:**
   - Выбрать "Полигон" в BrushTable
   - Кликнуть несколько раз по карте
   - Нажать "Добавить" (объект сохранится в БД)

2. **Редактирование стиля:**
   - В List.vue выбрать объект
   - Изменить цвет, прозрачность, пунктир
   - Изменения сохраняются автоматически

3. **Навигация:**
   - Кнопка "На карте" в List.vue приближает к объекту
   - Drag карты работает с grabCursor

## 🔧 Разработка

### Добавление нового слоя Deck.gl

1. Создать слой в `Map.vue`:
```typescript
new PolygonLayer({
  id: "my-layer",
  data: objects,
  getPolygon: (obj) => obj.coordinates,
  getFillColor: (obj) => obj.style.color,
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

## 🐛 Известные проблемы

### Курсоры
- Plus-cursor должен иметь hot spot `16 16`
- Применяются через CSS для `.maplibregl-canvas`

### Производительность
- При 50+ объектах возможны замедления
- `interleaved: true` может влиять на FPS

### Reactivity
- Watch за `Objects.value` может не срабатывать на мутации Map
- Использовать `Array.from(Objects.value.values())` для реактивности

## 🔗 Полезные ссылки

- [Deck.gl Documentation](https://deck.gl/docs)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js-docs/)
- [Vue 3 Guide](https://vuejs.org/guide/introduction.html)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [pywebview Docs](https://pywebview.flowrl.com/)
