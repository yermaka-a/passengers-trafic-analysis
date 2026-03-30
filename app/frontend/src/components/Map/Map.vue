<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl from "maplibre-gl";
import { storeToRefs } from "pinia";
import { useMapObjectStore, useMapStore } from "@/store";
import { useDeckGL } from "@/composables/useDeckGL";
import MapOptions from "./MapOptions.vue";
import PlusCursor from "@/assets/plus-cursor.svg";
import GrabCursor from "@/assets/grab-cursor.svg";
import type { LngLatTuple, DeckGLObject } from "@/types";
import { useTilesStore } from "@/store/useTilesStore";
import { generateIconAtlas } from "@/config/stopMarkers";

// Deck.gl imports
import { MapboxOverlay } from "@deck.gl/mapbox";
import { PolygonLayer, PathLayer, ScatterplotLayer, IconLayer } from "@deck.gl/layers";
import { PathStyleExtension } from "@deck.gl/extensions";
import { DeckGLMapConfig } from "@/config/DeckGLMapConfig";

const mapObjectStore = useMapObjectStore();
const mapStore = useMapStore();
const tilesStore = useTilesStore();

const { Objects, DraftObject } = storeToRefs(mapObjectStore);

// MapLibre instance
const mapInstance = ref<maplibregl.Map | null>(null);

// Deck.gl overlay
let deckOverlay: MapboxOverlay | null = null;

// Draft object color (default red)
const draftColor = ref("#ff0000");

// Coordinates display
const cursorCoords = ref<{ lat: number; lng: number } | null>(null);
const showCoordinates = ref(true);

// Popup для объектов
let popup: maplibregl.Popup | null = null;

// Convert hex to RGBA for Deck.gl
const hexToRGBA = (hex: string, alpha: number = 255): [number, number, number, number] => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return [255, 0, 0, alpha];
  return [
    Number.parseInt(result[1]!, 16),
    Number.parseInt(result[2]!, 16),
    Number.parseInt(result[3]!, 16),
    alpha,
  ];
};

// Курсоры
const plusCursor = computed(() => `url("${PlusCursor}") 16 16, auto`);
const grabCursor = computed(() => `url("${GrabCursor}") 16 16, auto`);

// L7 composable (переименовать потом в useDeckGL)
const {
  handleMapClick,
  finalizeObject: finalizeObjectFromComposable,
  cancelObject,
  undo,
  redo,
  canUndo,
  canRedo,
} = useDeckGL();

// Wrapper для передачи цвета
const finalizeObject = async () => {
  await finalizeObjectFromComposable(draftColor.value);
};

// Обновляем цвет draft объекта при изменении
watch(draftColor, (newColor) => {
  const draft = mapObjectStore.getDraftObject;
  if (draft) {
    const rgbaColor = hexToRGBA(newColor, 255);
    mapObjectStore.updateDraftStyle({ color: rgbaColor });
  }
});

// Обработка клика по карте
const onMapClick = (e: any) => {
  const lngLat: LngLatTuple = [e.lngLat.lng, e.lngLat.lat];
  console.log("[Map] Клик:", lngLat);
  handleMapClick(lngLat);
  
  // Закрываем popup при клике по карте
  closePopup();
};

// Выделение объекта при клике
const selectObject = (id: string) => {
  console.log("[Map] Select object:", id);
  mapObjectStore.ClickedObjId = id;
  
  // Показываем popup с информацией об объекте
  showObjectPopup(id);
};

// Генерация HTML для popup
const generatePopupContent = (obj: DeckGLObject): string => {
  const coords = obj.coordinates.map(([lng, lat], idx) => ({
    lat: lat.toFixed(8),
    lng: lng.toFixed(8),
    idx
  }));

  return `
    <div class="min-w-[280px] max-w-[320px] font-sans" data-object-id="${obj.id}">
      <!-- Header -->
      <div class="border-b pb-2 mb-2">
        <h3 class="font-semibold text-sm truncate" title="${obj.customName || obj.name}">${obj.customName || obj.name}</h3>
        <p class="text-xs text-gray-500 mt-0.5">${obj.type === 'Polygon' ? 'Полигон' : obj.type === 'Polyline' ? 'Полилиния' : 'Маркер'}</p>
      </div>
      
      <!-- Coordinates -->
      <div class="mb-3">
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-medium">📍 Координаты</span>
          <span class="text-xs text-gray-500">(${coords.length} точек)</span>
        </div>
        <div class="max-h-[100px] overflow-y-auto space-y-0.5 text-xs font-mono bg-gray-50 rounded p-1.5 border">
          ${coords.map(c => `
            <div class="flex justify-between items-center edit-coord-row" data-idx="${c.idx}" data-lat="${c.lat}" data-lng="${c.lng}">
              <span class="text-gray-600 truncate">#${c.idx + 1}:</span>
              <span class="coord-values truncate max-w-[120px]">${c.lat}, ${c.lng}</span>
              <button class="edit-coord-btn ml-1 text-blue-500 hover:text-blue-700 flex-shrink-0" data-idx="${c.idx}">✏️</button>
            </div>
          `).join('')}
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex gap-1.5 mt-2 pt-2 border-t">
        <button class="find-on-map-btn flex-1 text-xs px-2 py-1.5 rounded-md transition-colors text-white">
          Приблизить
        </button>
        <button class="close-popup-btn text-white w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0" style="background-color: #EF4444;">
          ✕
        </button>
      </div>
    </div>
  `;
};

// Показ popup для объекта
const showObjectPopup = (id: string) => {
  const obj = mapObjectStore.Objects.get(id);
  if (!obj || obj.coordinates.length === 0 || !mapInstance.value) return;

  const firstCoord = obj.coordinates[0];
  if (!firstCoord) return;
  
  const [lng, lat] = firstCoord;

  // Закрываем предыдущий popup
  if (popup) {
    popup.remove();
  }
  
  // Создаём новый popup
  popup = new maplibregl.Popup({
    closeButton: true,
    closeOnClick: true,
    maxWidth: '300px',
  })
  .setLngLat([lng, lat])
  .setHTML(generatePopupContent(obj))
  // @ts-ignore - mapInstance.value имеет правильный тип Map
  .addTo(mapInstance.value);
  
  // Добавляем обработчики для popup
  setTimeout(() => {
    // Hover эффекты для кнопок
    const primaryBtn = document.querySelector('.find-on-map-btn');
    if (primaryBtn) {
      primaryBtn.addEventListener('mouseenter', () => {
        (primaryBtn as HTMLElement).style.backgroundColor = '#0066CC';
      });
      primaryBtn.addEventListener('mouseleave', () => {
        (primaryBtn as HTMLElement).style.backgroundColor = '#0080FF';
      });
    }
    
    const dangerBtn = document.querySelector('.close-popup-btn');
    if (dangerBtn) {
      dangerBtn.addEventListener('mouseenter', () => {
        (dangerBtn as HTMLElement).style.backgroundColor = '#DC2626';
      });
      dangerBtn.addEventListener('mouseleave', () => {
        (dangerBtn as HTMLElement).style.backgroundColor = '#EF4444';
      });
    }
    
    // Кнопка "Приблизить"
    const findBtn = document.querySelector('.find-on-map-btn');
    if (findBtn) {
      findBtn.addEventListener('click', () => {
        mapStore.updateViewState({ latitude: lat, longitude: lng, zoom: 16 }, true);
        if (popup) popup.remove();
      });
    }
    
    // Кнопка "Закрыть"
    const closeBtn = document.querySelector('.close-popup-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        if (popup) popup.remove();
      });
    }
    
    // Кнопки редактирования координат - используем делегирование событий
    const coordsContainer = document.querySelector('.max-h-\\[100px\\]');
    if (coordsContainer) {
      coordsContainer.addEventListener('click', (e) => {
        const editBtn = (e.target as HTMLElement).closest('.edit-coord-btn');
        if (!editBtn) return;
        
        const row = editBtn.closest('.edit-coord-row') as HTMLElement;
        if (!row) return;
        
        // Проверяем, уже редактируется ли
        const existingInput = row.querySelector('.edit-lat-input');
        if (existingInput) return; // Уже редактируется
        
        const idx = row.dataset.idx;
        const currentLat = row.dataset.lat;
        const currentLng = row.dataset.lng;
        
        if (!idx || !currentLat || !currentLng) return;
        
        // Сохраняем оригинальный HTML для отмены
        const originalHTML = row.innerHTML;
        row.dataset.originalHtml = originalHTML;
        
        // Заменяем на input для редактирования
        row.innerHTML = `
          <span class="text-gray-600 truncate">#${Number(idx) + 1}:</span>
          <input type="text" class="edit-lat-input w-16 text-xs border rounded px-1 flex-shrink-0" value="${currentLat}" />
          <input type="text" class="edit-lng-input w-16 text-xs border rounded px-1 flex-shrink-0" value="${currentLng}" />
          <button class="save-edit-btn ml-1 text-green-600 hover:text-green-800 flex-shrink-0">✓</button>
          <button class="cancel-edit-btn ml-1 text-red-600 hover:text-red-800 flex-shrink-0">✗</button>
        `;
        
        // Обработчик сохранения
        const saveEditBtn = row.querySelector('.save-edit-btn') as HTMLButtonElement;
        saveEditBtn?.addEventListener('click', () => {
          const latInput = row.querySelector('.edit-lat-input') as HTMLInputElement;
          const lngInput = row.querySelector('.edit-lng-input') as HTMLInputElement;
          
          if (latInput && lngInput) {
            const newLat = latInput.value;
            const newLng = lngInput.value;
            row.dataset.lat = newLat;
            row.dataset.lng = newLng;
            
            // Обновляем координаты в store
            const obj = mapObjectStore.Objects.get(id);
            if (obj) {
              const newCoordinates = [...obj.coordinates];
              newCoordinates[Number(idx)] = [Number(newLng), Number(newLat)];
              mapObjectStore.updateObjectCoordinates(id, newCoordinates);

              // Принудительная перерисовка Deck.gl через публичный API
              if (deckOverlay) {
                deckOverlay.setProps({
                  layers: createDeckLayers(),
                });
              }
            }
          }
          
          // Восстанавливаем отображение
          row.innerHTML = `
            <span class="text-gray-600 truncate">#${Number(idx) + 1}:</span>
            <span class="coord-values truncate max-w-[120px]">${row.dataset.lat}, ${row.dataset.lng}</span>
            <button class="edit-coord-btn ml-1 text-blue-500 hover:text-blue-700 flex-shrink-0" data-idx="${idx}">✏️</button>
          `;
        });
        
        // Обработчик отмены
        const cancelEditBtn = row.querySelector('.cancel-edit-btn') as HTMLButtonElement;
        cancelEditBtn?.addEventListener('click', () => {
          // Восстанавливаем оригинальное отображение
          row.innerHTML = row.dataset.originalHtml || originalHTML;
        });
      });
    }
  }, 100);
};

// Закрыть popup при клике на карту
const closePopup = () => {
  if (popup) {
    popup.remove();
    popup = null;
  }
};

// Создание слоёв Deck.gl
const createDeckLayers = () => {
  const layers: any[] = [];

  const objectsArray = Array.from(Objects.value?.values() ?? []);
  console.log("[Map] createDeckLayers:", objectsArray.length, "объектов");

  // ========================================================================
  // СЛОИ ДЛЯ СУЩЕСТВУЮЩИХ ОБЪЕКТОВ
  // Порядок важен: сначала полигоны, потом линии, потом маркеры (поверх всех)
  // ========================================================================

  // 1. Polygon fill layer (и Polyline если filled=true) - самый нижний слой
  const polygonFillObjects = objectsArray.filter(
    (obj) => (obj.type === "Polygon" || obj.type === "Polyline") && obj.style.filled !== false
  );
  
  if (polygonFillObjects.length > 0) {
    layers.push(
      new PolygonLayer({
        id: "polygon-fill",
        data: polygonFillObjects,
        getPolygon: (obj: DeckGLObject) => obj.coordinates,
        getFillColor: (obj: DeckGLObject) => {
          // Применяем прозрачность fillOpacity к цвету
          const color = obj.style.color;
          return [
            color[0]!,
            color[1]!,
            color[2]!,
            Math.round(color[3]! * (obj.style.fillOpacity ?? 0.5))
          ] as [number, number, number, number];
        },
        updateTriggers: {
          getFillColor: polygonFillObjects.map(o => ({ id: o.id, color: o.style.color, fillOpacity: o.style.fillOpacity })),
        },
        getLineColor: [0, 0, 0, 0], // No outline from fill layer
        getElevation: 0,
        pickable: true,  // ✅ Заливка теперь кликабельна
        autoHighlight: false,  // Отключаем highlight
        onClick: (info: any) => {
          if (info.object) {
            selectObject((info.object as DeckGLObject).id);
          }
        },
        stroked: false,
        filled: true,
      })
    );
    console.log("[Map] Polygon fill слой добавлен");
  }

  // 2. Polygon/Polyline stroke layer - средний слой
  const lineObjects = objectsArray.filter(
    (obj) => obj.type === "Polygon" || obj.type === "Polyline"
  );

  if (lineObjects.length > 0) {
    console.log("[Map] Line объекты:", lineObjects.map(o => ({ 
      id: o.id, 
      color: o.style.color, 
      strokeWidth: o.style.strokeWidth,
      strokeDasharray: o.style.strokeDasharray 
    })));

    // Создаём PathStyleExtension для поддержки пунктира
    const pathStyleExtension = new PathStyleExtension({
      dash: true,
      highPrecisionDash: false,
    });

    // Логи для updateTriggers
    const dashTriggers = lineObjects.map(o => ({ id: o.id, strokeDasharray: o.style.strokeDasharray }));
    console.log("[Map] updateTriggers.getDashArray:", dashTriggers);

    layers.push(
      new PathLayer({
        id: "polygon-stroke",
        data: lineObjects,
        getPath: (obj: DeckGLObject) => obj.coordinates,
        getColor: (obj: DeckGLObject) => {
          console.log("[Map] getColor для", obj.id, ":", obj.style.color);
          return obj.style.color;
        },
        getWidth: (obj: DeckGLObject) => {
          console.log("[Map] getWidth для", obj.id, ":", obj.style.strokeWidth);
          return obj.style.strokeWidth ?? 2;
        },
        getDashArray: (obj: DeckGLObject) => {
          const dash = obj.style.strokeDasharray;
          console.log("[Map] getDashArray для", obj.id, ":", dash, "dash[0]:", dash?.[0]);
          // Возвращаем [0, 0] если пунктир выключен
          return dash && dash[0] && dash[0] > 0 ? dash : [0, 0];
        },
        updateTriggers: {
          getColor: lineObjects.map(o => ({ id: o.id, color: o.style.color })),
          getWidth: lineObjects.map(o => ({ id: o.id, strokeWidth: o.style.strokeWidth })),
          getDashArray: dashTriggers,
        },
        extensions: [pathStyleExtension],
        pickable: true,
        autoHighlight: true,
        onClick: (info: any) => {
          if (info.object) {
            selectObject((info.object as DeckGLObject).id);
          }
        },
      })
    );
    console.log("[Map] Line слой добавлен с PathStyleExtension");
  }

  // 3. CircleMarker layer - самый верхний слой (рисуется поверх всех)
  const pointObjects = objectsArray.filter(
    (obj) => obj.type === "CircleMarker"
  );

  if (pointObjects.length > 0) {
    // Сначала рисуем обводку (больший радиус)
    const objectsWithStroke = pointObjects.filter(
      (obj) => (obj.style.strokeWidth ?? 0) > 0
    );
    
    if (objectsWithStroke.length > 0) {
      layers.push(
        new ScatterplotLayer({
          id: "circle-marker-stroke",
          data: objectsWithStroke,
          getPosition: (obj: DeckGLObject) => obj.coordinates[0] ?? [0, 0],
          getFillColor: (obj: DeckGLObject) => obj.style.color,
          getLineColor: (obj: DeckGLObject) => obj.style.color,
          getRadius: (obj: DeckGLObject) => (obj.style.radius ?? 10) + (obj.style.strokeWidth ?? 0) / 2,
          radiusMinPixels: 5,
          radiusMaxPixels: 100,
          getLineWidth: (obj: DeckGLObject) => obj.style.strokeWidth ?? 0,
          getLineDashArray: (obj: DeckGLObject) => {
            const dash = obj.style.strokeDasharray;
            return dash && dash[0] && dash[0] > 0 ? dash : [0, 0];
          },
          updateTriggers: {
            getFillColor: objectsWithStroke.map(o => ({ id: o.id, color: o.style.color })),
            getLineColor: objectsWithStroke.map(o => ({ id: o.id, color: o.style.color })),
            getRadius: objectsWithStroke.map(o => ({ id: o.id, radius: o.style.radius, strokeWidth: o.style.strokeWidth })),
            getLineWidth: objectsWithStroke.map(o => ({ id: o.id, strokeWidth: o.style.strokeWidth })),
            getLineDashArray: objectsWithStroke.map(o => ({ id: o.id, strokeDasharray: o.style.strokeDasharray })),
          },
          pickable: false,  // Обводка не кликабельна, только fill
        })
      );
    }
    
    // Затем рисуем заливку (обычный радиус) - кликабельна
    layers.push(
      new ScatterplotLayer({
        id: "circle-marker-fill",
        data: pointObjects,
        getPosition: (obj: DeckGLObject) => obj.coordinates[0] ?? [0, 0],
        getFillColor: (obj: DeckGLObject) => {
          const color = obj.style.color;
          return [
            color[0]!,
            color[1]!,
            color[2]!,
            Math.round(color[3]! * (obj.style.fillOpacity ?? 1.0))
          ];
        },
        getLineColor: [0, 0, 0, 0],
        getRadius: (obj: DeckGLObject) => obj.style.radius ?? 10,
        radiusMinPixels: 5,
        radiusMaxPixels: 100,
        updateTriggers: {
          getFillColor: pointObjects.map(o => ({ id: o.id, color: o.style.color, fillOpacity: o.style.fillOpacity })),
          getRadius: pointObjects.map(o => ({ id: o.id, radius: o.style.radius })),
        },
        pickable: true,
        autoHighlight: true,
        onClick: (info: any) => {
          if (info.object) {
            selectObject((info.object as DeckGLObject).id);
          }
        },
      })
    );
    console.log("[Map] CircleMarker слой добавлен");
  }

  // 4. StopMarker layer - кластеризация через Deck.gl
  // На зумах < 5 показываем кластеры (круги с количеством)
  // На зумах 5+ показываем все иконки
  const stopMarkers = objectsArray.filter(
    (obj) => obj.type === "StopMarker" && mapObjectStore.visibleStopMarkerTypes.has(obj.markerType || 'pin')
  );

  const currentZoom = mapInstance.value?.getZoom() ?? 0;
  const showClusters = currentZoom < 5;

  if (stopMarkers.length > 0) {
    if (showClusters) {
      // Группируем маркеры по клеткам 10x10 пикселей
      const clusterSize = 10;
      const clusters = new Map<string, {
        count: number;
        centerLat: number;
        centerLng: number;
        lats: number[];
        lngs: number[];
      }>();

      stopMarkers.forEach(obj => {
        const coord = obj.coordinates[0];
        if (!coord) return;

        const [lng, lat] = coord;
        // Округляем до клетки
        const cellLat = Math.round(lat * clusterSize) / clusterSize;
        const cellLng = Math.round(lng * clusterSize) / clusterSize;
        const key = `${cellLat.toFixed(4)}-${cellLng.toFixed(4)}`;

        if (!clusters.has(key)) {
          clusters.set(key, {
            count: 0,
            centerLat: 0,
            centerLng: 0,
            lats: [],
            lngs: []
          });
        }

        const cluster = clusters.get(key)!;
        cluster.count++;
        cluster.lats.push(lat);
        cluster.lngs.push(lng);
      });

      // Вычисляем центры кластеров
      const clusterData = Array.from(clusters.entries()).map(([key, data]) => {
        const centerLat = data.lats.reduce((a, b) => a + b, 0) / data.lats.length;
        const centerLng = data.lngs.reduce((a, b) => a + b, 0) / data.lngs.length;
        return {
          position: [centerLng, centerLat],
          count: data.count,
          key
        };
      });

      // ScatterplotLayer для кругов кластеров
      layers.push(
        new ScatterplotLayer({
          id: "stop-markers-clusters",
          data: clusterData,
          getPosition: (d: any) => d.position,
          getFillColor: (d: any) => {
            const count = d.count;
            if (count < 10) return [0, 188, 212, 220];      // голубой
            if (count < 50) return [255, 152, 0, 220];      // оранжевый
            return [244, 67, 54, 220];                       // красный
          },
          getRadius: (d: any) => Math.max(30, Math.min(80, 25 + d.count)),
          getLineColor: [255, 255, 255],
          getLineWidth: 3,
          pickable: true,
          onClick: (info: any) => {
            if (info.object) {
              // Зум на кластер
              mapInstance.value?.flyTo({
                center: [info.object.position[0], info.object.position[1]],
                zoom: Math.min(currentZoom + 2, 16)
              });
              console.log(`[Map] Cluster: ${info.object.count} остановок`);
            }
          }
        })
      );
    } else {
      // Показываем все иконки на зумах 5+
      const { atlas: iconAtlas, mapping: iconMapping } = generateIconAtlas();

      layers.push(
        new IconLayer({
          id: "stop-markers",
          data: stopMarkers,
          iconAtlas,
          iconMapping,
          getIcon: (obj: DeckGLObject) => {
            const type = obj.markerType || 'pin';
            return iconMapping[type] ? type : 'pin';
          },
          getPosition: (obj: DeckGLObject) => obj.coordinates[0] ?? [0, 0],
          getSize: (obj: DeckGLObject) => {
            const scale = obj.style.getSizeScale || 1.5;
            return 24 * scale;
          },
          sizeScale: 1,
          sizeMinPixels: 10,
          sizeMaxPixels: 100,
          getColor: (obj: DeckGLObject) => obj.style.color,
          pickable: true,
          autoHighlight: true,
          onClick: (info: any) => {
            if (info.object) {
              selectObject((info.object as DeckGLObject).id);
            }
          },
          updateTriggers: {
            getIcon: stopMarkers.map(o => ({ id: o.id, markerType: o.markerType })),
            getPosition: stopMarkers.map(o => ({ id: o.id, coordinates: o.coordinates[0] })),
            getColor: stopMarkers.map(o => ({ id: o.id, color: o.style.color })),
            getSize: stopMarkers.map(o => ({ id: o.id, getSizeScale: o.style.getSizeScale, radius: o.style.radius })),
          }
        })
      );
    }
  }

  // ========================================================================
  // СЛОЙ ДЛЯ DRAFT ОБЪЕКТА (в процессе создания)
  // ========================================================================

  if (DraftObject.value && DraftObject.value.coordinates.length > 0) {
    const draft = DraftObject.value;
    // Используем цвет из state
    const draftColorRGBA = hexToRGBA(draftColor.value, 255);
    const draftColorRGBATransparent = hexToRGBA(draftColor.value, 100);

    // StopMarker - 1 точка с иконкой
    if (draft.type === "StopMarker" && draft.coordinates.length > 0) {
      const markerType = (draft as any).markerType || 'bus';
      const { atlas: iconAtlas, mapping: iconMapping } = generateIconAtlas();
      
      console.log("[Map] Draft StopMarker:", {
        markerType,
        coordinates: draft.coordinates[0],
        iconMapping: Object.keys(iconMapping),
        iconAtlasLength: iconAtlas.length
      });
      
      layers.push(
        new IconLayer({
          id: "draft-stop-marker",
          data: [draft],
          // @ts-ignore - используем iconAtlas с mask: true
          iconAtlas,
          // @ts-ignore - iconMapping для всех типов
          iconMapping,
          getIcon: () => markerType,
          getPosition: (d: typeof draft) => d.coordinates[0] ?? [0, 0],
          getSize: 24,
          getColor: draftColorRGBA,
          getSizeScale: 1.5,
          pickable: false,
        })
      );
      console.log("[Map] Draft StopMarker слой добавлен, тип:", markerType);
    }
    
    // CircleMarker - даже с 1 точкой
    else if (draft.type === "CircleMarker" && draft.coordinates.length > 0) {
      layers.push(
        new ScatterplotLayer({
          id: "draft-circle",
          data: [draft],
          getPosition: (d: typeof draft) => d.coordinates[0] ?? [0, 0],
          getColor: draftColorRGBA,
          getRadius: 15,
          radiusMinPixels: 10,
          pickable: false,
        })
      );
    }
    // Polygon/Polyline - минимум 2 точки
    else if (draft.coordinates.length >= 2) {
      // Line layer для контура
      layers.push(
        new PathLayer({
          id: "draft-line",
          data: [draft],
          getPath: (d: typeof draft) => d.coordinates,
          getColor: draftColorRGBA,
          getWidth: 3,
          pickable: false,
        })
      );

      // Polygon fill - если >= 3 точек
      if (draft.type === "Polygon" && draft.coordinates.length >= 3) {
        layers.push(
          new PolygonLayer({
            id: "draft-polygon-fill",
            data: [draft],
            getPolygon: (d: typeof draft) => d.coordinates,
            getFillColor: draftColorRGBATransparent,
            getLineColor: [0, 0, 0, 0],
            pickable: false,
          })
        );
      }
    }
  }

  return layers;
};

// Инициализация карты
onMounted(() => {
  console.log("[Map] onMounted - начинаем инициализацию");
  
  try {
    // Создаём MapLibre map
    const map = new maplibregl.Map({
      container: "map",
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: [
              "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
              "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
              "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
            ],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap contributors',
          },
        },
        layers: [
          {
            id: "osm-tiles",
            type: "raster",
            source: "osm",
          },
        ],
      },
      center: [
        DeckGLMapConfig.initialViewState.longitude,
        DeckGLMapConfig.initialViewState.latitude,
      ],
      zoom: DeckGLMapConfig.initialViewState.zoom,
      pitch: DeckGLMapConfig.initialViewState.pitch,
      bearing: DeckGLMapConfig.initialViewState.bearing,
    });

    // Сохраняем instance
    mapInstance.value = map;
    // @ts-ignore - сохраняем ссылку для доступа из List.vue
    mapStore.mapInstance = map;
    // @ts-ignore - устанавливаем функцию для popup
    mapStore.showObjectPopupRef = showObjectPopup;
    console.log("[Map] MapLibre создана");

    // === КЛАСТЕРИЗАЦИЯ ЧЕРЕЗ DECK.GL (вместо MapLibre) ===
    // MapLibre кластеризация конфликтует с Deck.gl overlay
    // Вместо этого скрываем маркеры на зумах < 14

    // Слушаем событие переключения тайлов из List.vue
    window.addEventListener('map-tiles-change', (event: any) => {
      if (!mapInstance.value) return;
      const config = event.detail;
      
      console.log('[Map] map-tiles-change:', config);
      
      // Для векторных стилей (OpenFreeMap)
      if (config.type === 'vector' && config.style) {
        console.log('[Map] Switching to vector style:', config.style);
        mapInstance.value.setStyle(config.style as any);
        return;
      }
      
      // Для растровых тайлов
      const style = mapInstance.value.getStyle();
      if (style.sources?.["osm"] && "tiles" in style.sources["osm"]) {
        (style.sources["osm"] as any).tiles = config.tiles;
        (style.sources["osm"] as any).attribution = config.attribution;
        mapInstance.value.setStyle(style);
      }
    });

    // Слушаем изменения слоя карт от других окон
    window.addEventListener('panel-sync', (event: any) => {
      if (event.detail?.type === 'TILE_LAYER_CHANGED') {
        const layer = event.detail.data?.layer;
        console.log('[Map] Received TILE_LAYER_CHANGED:', layer, 'current:', tilesStore.currentLayer);
        if (layer && tilesStore.currentLayer !== layer) {
          tilesStore.setLayer(layer);
          // Применяем слой
          const config = tilesStore.getCurrentLayerConfig();
          console.log('[Map] Applying config:', config);
          
          // Для векторных стилей - применяем style напрямую
          if (config.type === 'vector' && config.style) {
            console.log('[Map] Switching to vector style:', config.style);
            mapInstance.value?.setStyle(config.style as any);
            console.log('[Map] Vector style applied successfully!');
            return;
          }
          
          // Для растровых тайлов
          const style = mapInstance.value?.getStyle();
          if (style && style.sources?.["osm"] && "tiles" in style.sources["osm"]) {
            (style.sources["osm"] as any).tiles = config.tiles;
            (style.sources["osm"] as any).attribution = config.attribution;
            mapInstance.value?.setStyle(style);
            console.log('[Map] Layer applied successfully!');
          }
        }
      }
    });

    // Создаём Deck.gl overlay
    deckOverlay = new MapboxOverlay({
      layers: createDeckLayers(),
      interleaved: true, // Важно для правильной отрисовки с MapLibre
    });

    // Добавляем Deck.gl как control
    map.addControl(deckOverlay);
    console.log("[Map] Deck.gl overlay добавлен");

    // Добавляем обработчик клика
    map.on("click", onMapClick);
    console.log("[Map] MapLibre click обработчик добавлен");

    // Обработчик изменения зума для обновления кластеров
    let zoomTimeout: ReturnType<typeof setTimeout>;
    map.on('zoom', () => {
      clearTimeout(zoomTimeout);
      zoomTimeout = setTimeout(() => {
        if (deckOverlay) {
          deckOverlay.setProps({
            layers: createDeckLayers()
          });
        }
      }, 100);
    });

    // === КЛАСТЕРИЗАЦИЯ ЧЕРЕЗ SUPERCLUSTER ===
    // Zoom 0-4: кластеры (круги с цифрами)
    // Zoom 5+: все точки остановок

    // Обработчик движения мыши для отображения координат
    map.on("mousemove", (e: any) => {
      cursorCoords.value = {
        lat: e.lngLat.lat,
        lng: e.lngLat.lng,
      };
    });

    // Очистка координат при выходе мыши из карты
    map.on("mouseleave", () => {
      cursorCoords.value = null;
    });

    // Применяем стили для курсоров через CSS
    // Курсоры управляются через CSS классы maplibregl-map и maplibregl-canvas:active

    // Watch для реактивности - перерисовка при изменении объектов
    // Используем Array.from для реактивности Map
    watch(
      () => Array.from(Objects.value?.values() ?? []),
      () => {
        // Принудительно обновляем layers для Deck.gl через публичный API
        if (deckOverlay) {
          deckOverlay.setProps({
            layers: createDeckLayers(),
          });
        }
      },
      { deep: true },
    );
    
    // Watch для переключения слоёв карты
    watch(
      () => tilesStore.currentLayer,
      (newLayer, oldLayer) => {
        if (newLayer === oldLayer) return; // Пропускаем одинаковые изменения
        
        console.log('[Map] Tile layer changed to:', newLayer);
        const config = tilesStore.getCurrentLayerConfig();
        
        // Для векторных стилей - применяем style напрямую
        if (config.type === 'vector' && config.style) {
          console.log('[Map] Switching to vector style via watch:', config.style);
          mapInstance.value?.setStyle(config.style as any);
          console.log('[Map] Vector style applied via watch!');
          return;
        }
        
        // Для растровых тайлов
        const style = mapInstance.value?.getStyle();
        if (style && style.sources?.["osm"] && "tiles" in style.sources["osm"]) {
          (style.sources["osm"] as any).tiles = config.tiles;
          (style.sources["osm"] as any).attribution = config.attribution;
          mapInstance.value?.setStyle(style);
          console.log('[Map] Layer applied via watch!');
        }
      },
    );

    // Watch для draft объекта
    watch(
      () => DraftObject.value,
      (newDraft) => {
        console.log(
          "[Map] Draft объект изменился:",
          newDraft?.coordinates.length ?? 0,
          "точек",
        );
        if (deckOverlay) {
          deckOverlay.setProps({
            layers: createDeckLayers(),
          });
        }
      },
      { deep: true },
    );
  } catch (error) {
    console.error("[Map] Ошибка инициализации:", error);
  }
});

// Очистка при размонтировании
onUnmounted(() => {
  console.log("[Map] onUnmounted - очистка");
  if (popup) {
    popup.remove();
    popup = null;
  }
  if (deckOverlay) {
    deckOverlay.finalize();
    deckOverlay = null;
  }
  if (mapInstance.value) {
    mapInstance.value.remove();
    mapInstance.value = null;
  }
});
</script>

<template>
  <MapOptions
    :cancel-changes="cancelObject"
    :submit-changes="finalizeObject"
    :prev-action="undo"
    :next-action="redo"
    :can-undo="canUndo"
    :can-redo="canRedo"
    :draft-color="draftColor"
    :show-coordinates="showCoordinates"
    @update:draft-color="draftColor = $event"
    @update:show-coordinates="showCoordinates = $event"
  />
  <div class="flex-1 h-screen overflow-scroll">
    <div
      id="map"
      class="relative"
    >
      <!-- Отображение координат курсора -->
      <div
        v-if="showCoordinates && cursorCoords"
        class="absolute top-4 left-4 bg-white/90 backdrop-blur-sm border border-gray-200 rounded-md px-3 py-2 text-xs font-mono shadow-lg z-50 pointer-events-none"
      >
        <span class="text-gray-600">Широта:</span>
        <span class="ml-2 font-medium">{{ cursorCoords.lat.toFixed(8) }}</span>
        <span class="mx-2 text-gray-400">|</span>
        <span class="text-gray-600">Долгота:</span>
        <span class="ml-2 font-medium">{{ cursorCoords.lng.toFixed(8) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(#map) {
  height: 100vh;
  width: 100vw;
  outline: none;
  user-select: none;
  position: relative;
  cursor: v-bind(plusCursor) !important;
}

:deep(.maplibregl-map) {
  cursor: v-bind(plusCursor) !important;
}

:deep(.maplibregl-canvas) {
  cursor: v-bind(plusCursor) !important;
}

:deep(.maplibregl-canvas:active),
:deep(.maplibregl-map.dragging) {
  cursor: v-bind(grabCursor) !important;
}

/* Deck.gl canvas должен быть поверх MapLibre */
:deep(.deckgl-overlay) {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  z-index: 10 !important;
  pointer-events: none !important;
}
</style>
