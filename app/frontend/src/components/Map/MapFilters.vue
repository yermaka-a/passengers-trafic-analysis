<script setup lang="ts">
import { computed } from "vue";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Filter } from "lucide-vue-next";

const mapObjectStore = useMapObjectStore();
const visibleTypes = computed(() => mapObjectStore.getVisibleStopMarkerTypes);

const markerTypes = [
  { id: 'pin', label: '📍 Маркер' },
  { id: 'pinned', label: '📌 Закреплён' },
  { id: 'flag', label: '🚩 Флаг' },
  { id: 'flag-check', label: '🚩✓ Флаг (отмечен)' },
  { id: 'pin-check', label: '📍✓ Маркер (отмечен)' },
  { id: 'pin-plus', label: '📍+ Маркер (+)' },
  { id: 'balloon', label: '🎈 Шарик' },
];

const toggleType = (type: string) => {
  mapObjectStore.toggleStopMarkerType(type);
};

const allVisible = computed(() => markerTypes.every(t => visibleTypes.value.has(t.id)));
const noneVisible = computed(() => markerTypes.every(t => !visibleTypes.value.has(t.id)));

const toggleAll = () => {
  if (allVisible.value) {
    // Скрыть все
    mapObjectStore.setVisibleStopMarkerTypes(new Set());
  } else {
    // Показать все
    mapObjectStore.setVisibleStopMarkerTypes(new Set(markerTypes.map(t => t.id)));
  }
};
</script>

<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="outline" size="sm" class="flex items-center gap-2">
        <Filter class="w-4 h-4" />
        Фильтры
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-64">
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="text-sm font-medium">Типы маркеров</h4>
          <Button variant="ghost" size="sm" @click="toggleAll" class="h-6 text-xs">
            {{ allVisible ? 'Скрыть все' : noneVisible ? 'Показать все' : 'Сбросить' }}
          </Button>
        </div>
        
        <div class="space-y-2">
          <div
            v-for="type in markerTypes"
            :key="type.id"
            class="flex items-center space-x-2"
          >
            <Checkbox
              :id="type.id"
              :checked="visibleTypes.has(type.id)"
              @update:checked="toggleType(type.id)"
            />
            <Label
              :for="type.id"
              class="text-sm font-normal cursor-pointer flex-1"
            >
              {{ type.label }}
            </Label>
          </div>
        </div>
      </div>
    </PopoverContent>
  </Popover>
</template>
