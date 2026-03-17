# Проект: Passenger Traffic Analysis

## Архитектура

- **Frontend:** Vue 3 + Vite (порт 5173)
- **Backend:** Python + pywebview (SQLite + SQLAlchemy)
- **API:** Доступно только через `window.pywebview.api` когда приложение запущено через pywebview
- **Карты:** MapLibre GL JS + AntV L7 (проблема с WebGL рендерингом)

## Команды запуска

### `yarn dev`
Запускает **только frontend** (Vite dev server). 
- ✅ Карты работают, слои L7 отображаются
- ✅ Объекты создаются в memory store
- ❌ **Сохранение в БД НЕ работает** (ошибка `pywebview is not registered`)

### `python main.py` (из корня проекта)
Запускает **Python backend + pywebview окно** с frontend.
- ✅ Frontend внутри приложения pywebview
- ✅ API доступно через `window.pywebview.api`
- ✅ Сохранение в БД работает

### `yarn dev:all`
Запускает **frontend + Python backend** одновременно через concurrently.
- ⚠️ Backend пытается открыть pywebview окно
- ⚠️ Frontend доступен в браузере на localhost:5173
- ❌ Frontend в браузере **НЕ ИМЕЕТ доступа к API** (только внутри pywebview окна)

### `yarn build`
Сборка проекта для продакшена.

## Важные заметки

- Для **сохранения объектов в базу данных** запускайте `python main.py` из корня проекта
- Ошибка `pywebview is not registered` означает, что frontend запущен в браузере, а не внутри pywebview приложения
- Для **тестирования UI и создания объектов** можно использовать `yarn dev`, но данные сохранятся только в memory store
- После перезагрузки страницы при `yarn dev` все созданные объекты пропадут (не сохранены в БД)

## Проблемы миграции на L7

### Проблема: L7 слои не рендерятся

**Симптомы:**
- Слои создаются (`scene.addLayer()` работает)
- `scene.getLayers()` показывает слои
- Но слои **не видны на карте**
- WebGL контекст не создаётся для L7 canvas

**Причина:**
`@antv/l7-maps` MapLibre adapter не создаёт WebGL контекст корректно. MapLibre создаёт свой canvas для рендеринга карты, но L7 не может создать свой WebGL canvas поверх.

**Попытки решения:**
1. ✅ Конвертация координат из Proxy в чистые массивы
2. ✅ Создание слоёв для draft объектов
3. ✅ watch для реактивности
4. ❌ MapLibre adapter - не работает WebGL
5. ❌ Готовый style URL - не работает WebGL

**Варианты решения:**
1. Использовать L7 без MapLibre adapter (создать сцену напрямую)
2. Использовать другой adapter (например, `@antv/l7-mapbox` с mapbox-gl)
3. Вернуться к Deck.gl + Leaflet
4. Использовать L7Draw для рисования поверх карты
