<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue";
import { ObjectListView, PropertyTable } from "@/components/ObjectList";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { useMapStore } from "@/store";
import { storeToRefs } from "pinia";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { LayoutGrid, Table as TableIcon, ChevronDown, ChevronUp, Search, Download, Upload, Import, FileJson } from "lucide-vue-next";
import { useTilesStore } from "@/store/useTilesStore";
import type { TileLayer } from "@/store/useTilesStore";
import OverpassImport from "@/components/OverpassImport/OverpassImport.vue";
import BulkExportImport from "@/components/BulkExportImport/BulkExportImport.vue";

type ViewType = "cards" | "table";

const mapObjectStore = useMapObjectStore();
const { Objects } = storeToRefs(mapObjectStore);
const mapStore = useMapStore();
const tilesStore = useTilesStore();

const view = ref<ViewType>("cards");
const showTilesMenu = ref(false);
const tilesMenuRef = ref<HTMLElement | null>(null);
const showViewMenu = ref(false);
const viewMenuRef = ref<HTMLElement | null>(null);
const showImportExportMenu = ref(false);
const importExportMenuRef = ref<HTMLElement | null>(null);
const showBulkExportImport = ref(false);
const sortDescending = ref(true); // true = новые сверху

// Сортировка объектов
const sortedObjects = computed(() => {
  const sorted = [...filteredObjects.value];
  sorted.sort((a, b) => {
    // Сортируем по ID (UUID v6 имеет временную метку в начале)
    const idA = a[0];
    const idB = b[0];
    if (sortDescending.value) {
      return idB.localeCompare(idA);
    } else {
      return idA.localeCompare(idB);
    }
  });
  return sorted;
});

// Импорт остановок
const showImportDialog = ref(false);

const handleImported = async () => {
  console.log("[List] Остановки импортированы, обновляем...");
  await mapObjectStore.loadAllObjectsFromDB();
};

// Обработчик импорта геометрии
const handleGeometryImported = async () => {
  console.log("[List] Геометрия импортирована, обновляем...");
  await mapObjectStore.loadAllObjectsFromDB();
};

// Экспорт остановок
const handleExportStops = async () => {
  showImportExportMenu.value = false;
  
  try {
    const result = await (window as any).pywebview.api.export_stops({});

    if (result.status === "success") {
      console.log(`[List] Экспортировано ${result.count} остановок в ${result.message}`);
      alert(`✅ ${result.message}`);
    } else if (result.status === "cancelled") {
      console.log("[List] Экспорт отменён пользователем");
    } else {
      console.error("Ошибка экспорта:", result.message);
      alert(`❌ Ошибка: ${result.message}`);
    }
  } catch (e) {
    console.error("Ошибка экспорта:", e);
    alert(`❌ Ошибка: ${e}`);
  }
};

// Фильтры
const filterType = ref<string>("all");
const searchQuery = ref<string>("");

// Фильтрация объектов
const filteredObjects = computed(() => {
  const allObjects = Array.from(Objects.value?.entries() ?? []);

  return allObjects.filter(([_, obj]) => {
    // Фильтр по типу
    const typeMatch = filterType.value === "all" || obj.type === filterType.value;

    // Поиск по имени
    const searchLower = searchQuery.value.toLowerCase();
    const nameMatch = !searchQuery.value ||
      (obj.customName && obj.customName.toLowerCase().includes(searchLower)) ||
      (obj.description && obj.description.toLowerCase().includes(searchLower)) ||
      obj.name.toLowerCase().includes(searchLower);

    return typeMatch && nameMatch;
  });
});

// Загружаем предпочтения из localStorage
onMounted(() => {
  const savedView = localStorage.getItem("objectListView") as ViewType;
  if (savedView === "cards" || savedView === "table") {
    view.value = savedView;
  }

  // Обработчик клика вне dropdown
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

const handleClickOutside = (event: MouseEvent) => {
  if (showTilesMenu.value && tilesMenuRef.value && !tilesMenuRef.value.contains(event.target as Node)) {
    showTilesMenu.value = false;
  }
  if (showViewMenu.value && viewMenuRef.value && !viewMenuRef.value.contains(event.target as Node)) {
    showViewMenu.value = false;
  }
  if (showImportExportMenu.value && importExportMenuRef.value && !importExportMenuRef.value.contains(event.target as Node)) {
    showImportExportMenu.value = false;
  }
};

// Сохраняем выбор в localStorage
const setView = (newView: ViewType) => {
  view.value = newView;
  localStorage.setItem("objectListView", newView);
};

const switchLayer = async (layer: TileLayer) => {
  tilesStore.setLayer(layer);
  showTilesMenu.value = false;
  
  const config = tilesStore.getCurrentLayerConfig();
  console.log('[List] Switching to layer:', layer, config);
  
  // Сохраняем через useApi для синхронизации между окнами
  const useApiModule = await import('@/composables/useApi');
  const { setCurrentTileLayer } = useApiModule.default();
  try {
    const result = await setCurrentTileLayer(layer);
    console.log('[List] Tile layer saved:', result);
  } catch (e) {
    console.error('[List] Error saving tile layer:', e);
  }
  
  // Отправляем событие для переключения тайлов
  window.dispatchEvent(new CustomEvent('map-tiles-change', {
    detail: config
  }));
};

// Открыть popup для объекта
const openObjectPopup = (id: string) => {
  mapStore.openPopup(id);
};
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Переключатель вида и тайлов -->
    <div class="flex flex-wrap items-center justify-between gap-3 px-8 py-4 border-b">
      <h1 class="text-2xl font-semibold">Объекты на карте</h1>
      <div class="flex flex-wrap items-center gap-2">
        <!-- Фильтры -->
        <div class="flex items-center gap-2 mr-auto">
          <Select v-model="filterType">
            <SelectTrigger class="w-[150px]">
              <SelectValue placeholder="Все типы" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Все типы</SelectItem>
              <SelectItem value="Polygon">Полигоны</SelectItem>
              <SelectItem value="Polyline">Полилинии</SelectItem>
              <SelectItem value="CircleMarker">Маркеры-круг</SelectItem>
              <SelectItem value="StopMarker">Маркеры</SelectItem>
            </SelectContent>
          </Select>
          
          <div class="relative">
            <Search class="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
            <Input
              v-model="searchQuery"
              placeholder="Поиск по названию..."
              class="pl-8 w-[200px]"
            />
          </div>
        </div>
        
        <!-- Переключатель тайлов -->
        <div ref="tilesMenuRef" class="relative">
          <Button
            variant="outline"
            size="sm"
            @click="showTilesMenu = !showTilesMenu"
            class="flex items-center gap-2"
          >
            <ChevronDown class="w-4 h-4" :class="{ 'rotate-180': showTilesMenu }" />
            Слои карты
          </Button>

          <!-- Выпадающее меню -->
          <div
            v-if="showTilesMenu"
            class="absolute right-0 top-full mt-1 bg-white border rounded-md shadow-lg z-50 min-w-[150px]"
          >
            <button
              v-for="(layer, key) in tilesStore.layers"
              :key="key"
              @click="switchLayer(key as TileLayer)"
              :class="[
                'w-full px-4 py-2 text-left text-sm hover:bg-accent transition-colors',
                tilesStore.currentLayer === key ? 'bg-accent font-medium' : ''
              ]"
            >
              {{ layer.name }}
            </button>
          </div>
        </div>

        <!-- Импорт/Экспорт -->
        <div ref="importExportMenuRef" class="relative">
          <Button
            variant="outline"
            size="sm"
            @click="showImportExportMenu = !showImportExportMenu"
            class="flex items-center gap-2"
          >
            <Import class="w-4 h-4" />
            Объекты
            <ChevronDown class="w-4 h-4" :class="{ 'rotate-180': showImportExportMenu }" />
          </Button>

          <!-- Выпадающее меню -->
          <div
            v-if="showImportExportMenu"
            class="absolute right-0 top-full mt-1 bg-white border rounded-md shadow-lg z-50 min-w-[220px]"
          >
            <div class="px-3 py-2 text-xs font-medium text-muted-foreground border-b">
              Остановки
            </div>
            <button
              @click="showImportDialog = true; showImportExportMenu = false"
              class="w-full px-4 py-2 text-left text-sm hover:bg-accent transition-colors flex items-center gap-2"
            >
              <Download class="w-4 h-4" />
              Импорт
            </button>
            <button
              @click="handleExportStops"
              class="w-full px-4 py-2 text-left text-sm hover:bg-accent transition-colors flex items-center gap-2"
            >
              <Upload class="w-4 h-4" />
              Экспорт
            </button>
            <div class="px-3 py-2 text-xs font-medium text-muted-foreground border-b border-t">
              Геометрия (Полигоны/Полилинии)
            </div>
            <button
              @click="showBulkExportImport = true; showImportExportMenu = false"
              class="w-full px-4 py-2 text-left text-sm hover:bg-accent transition-colors flex items-center gap-2"
            >
              <FileJson class="w-4 h-4" />
              Импорт/Экспорт
            </button>
          </div>
        </div>

        <!-- Переключатель вида -->
        <div ref="viewMenuRef" class="relative">
          <Button
            variant="outline"
            size="sm"
            @click="showViewMenu = !showViewMenu"
            class="flex items-center gap-2"
          >
            <component :is="view === 'cards' ? LayoutGrid : TableIcon" class="w-4 h-4" />
            {{ view === 'cards' ? 'Карточки' : 'Таблица' }}
            <ChevronDown class="w-4 h-4" :class="{ 'rotate-180': showViewMenu }" />
          </Button>

          <!-- Выпадающее меню -->
          <div
            v-if="showViewMenu"
            class="absolute right-0 top-full mt-1 bg-white border rounded-md shadow-lg z-50 min-w-[180px]"
          >
            <button
              @click="setView('cards'); showViewMenu = false"
              :class="[
                'w-full px-4 py-2 text-left text-sm hover:bg-accent transition-colors flex items-center gap-2',
                view === 'cards' ? 'bg-accent font-medium' : ''
              ]"
            >
              <LayoutGrid class="w-4 h-4" />
              Карточки
            </button>
            <button
              @click="setView('table'); showViewMenu = false"
              :class="[
                'w-full px-4 py-2 text-left text-sm hover:bg-accent transition-colors flex items-center gap-2',
                view === 'table' ? 'bg-accent font-medium' : ''
              ]"
            >
              <TableIcon class="w-4 h-4" />
              Таблица
            </button>
            <hr class="my-1" />
            <button
              @click="sortDescending = !sortDescending; showViewMenu = false"
              class="w-full px-4 py-2 text-left text-sm hover:bg-accent transition-colors flex items-center gap-2"
            >
              <component :is="sortDescending ? ChevronDown : ChevronUp" class="w-4 h-4" />
              {{ sortDescending ? 'Сначала новые' : 'Сначала старые' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Контент -->
    <div class="flex-1 overflow-auto">
      <ObjectListView
        v-if="view === 'cards'"
        :objects="sortedObjects"
        @open-popup="openObjectPopup"
      />
      <PropertyTable
        v-else
        :objects="sortedObjects"
        @open-popup="openObjectPopup"
      />
    </div>
    
    <!-- Dialog импорта остановок -->
    <OverpassImport
      v-model:open="showImportDialog"
      @imported="handleImported"
    />

    <!-- Dialog импорта/экспорта геометрии -->
    <BulkExportImport
      v-model:open="showBulkExportImport"
      @imported="handleGeometryImported"
    />
  </div>
</template>

<style scoped>
/* Анимация переключения */
.view-transition {
  transition: opacity 0.2s ease-in-out;
}
</style>
