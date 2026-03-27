<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue";
import { ObjectListView, PropertyTable } from "@/components/ObjectList";
import { useMapObjectStore } from "@/store/useMapObjectStore";
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
import { LayoutGrid, Table as TableIcon, ChevronDown, Search } from "lucide-vue-next";
import { useTilesStore } from "@/store/useTilesStore";
import type { TileLayer } from "@/store/useTilesStore";

type ViewType = "cards" | "table";

const mapObjectStore = useMapObjectStore();
const { Objects } = storeToRefs(mapObjectStore);
const tilesStore = useTilesStore();

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
};

// Сохраняем выбор в localStorage
const setView = (newView: ViewType) => {
  view.value = newView;
  localStorage.setItem("objectListView", newView);
};

const switchLayer = (layer: TileLayer) => {
  tilesStore.setLayer(layer);
  showTilesMenu.value = false;
  // Сообщаем карте что нужно обновить тайлы
  window.dispatchEvent(new CustomEvent('map-tiles-change', { 
    detail: tilesStore.getCurrentLayerConfig() 
  }));
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
              <SelectItem value="CircleMarker">Маркеры</SelectItem>
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
        
        <!-- Переключатель вида -->
        <Button
          variant="outline"
          size="sm"
          :class="view === 'cards' ? 'bg-accent' : ''"
          @click="setView('cards')"
          title="Вид: Карточки"
        >
          <LayoutGrid class="w-4 h-4 mr-2" />
          Карточки
        </Button>
        <Button
          variant="outline"
          size="sm"
          :class="view === 'table' ? 'bg-accent' : ''"
          @click="setView('table')"
          title="Вид: Таблица"
        >
          <TableIcon class="w-4 h-4 mr-2" />
          Таблица
        </Button>
      </div>
    </div>

    <!-- Контент -->
    <div class="flex-1 overflow-hidden">
      <ObjectListView v-if="view === 'cards'" :objects="filteredObjects" />
      <PropertyTable v-else :objects="filteredObjects" />
    </div>
  </div>
</template>

<style scoped>
/* Анимация переключения */
.view-transition {
  transition: opacity 0.2s ease-in-out;
}
</style>
