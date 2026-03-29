<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { ButtonGroup } from "@/components/ui/button-group";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { STOP_MARKER_ICONS, type StopMarkerType } from "@/config/stopMarkers";
import { ref, computed, watch } from "vue";

const mapObjectStore = useMapObjectStore();

const selectedMarkerType = ref<StopMarkerType>('pin');

// Сохраняем выбранный тип маркера глобально для доступа из useDeckGL
watch(selectedMarkerType, (newValue) => {
  (window as any).__selectedMarkerType = newValue;
});

const isActive = (option: (typeof mapObjectStore.getObjectsTypes)[number]) => {
  return option[1] === mapObjectStore.getChosenObjectType[1];
};

const isStopMarkerSelected = computed(() => {
  return mapObjectStore.getChosenObjectType[0] === 'StopMarker';
});
</script>

<template>
  <div class="space-y-2">
    <ButtonGroup class="w-full flex flex-wrap">
      <Button
        v-for="option in mapObjectStore.getObjectsTypes"
        :key="option[1]"
        size="lg"
        variant="outline"
        class="cursor-pointer"
        :class="{
          'bg-emerald-100 hover:bg-emerald-200': isActive(option),
        }"
        :disabled="mapObjectStore.getDraftObject !== null"
        @click="
          () => {
            mapObjectStore.setObjectType(option);
            mapObjectStore.cancelDraftObject();
          }
        "
      >
        {{ option[1] }}
      </Button>
    </ButtonGroup>

    <!-- Выбор типа маркера для StopMarker -->
    <Select v-if="isStopMarkerSelected" v-model="selectedMarkerType">
      <SelectTrigger class="w-[180px]">
        <SelectValue placeholder="Выберите тип маркера" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Тип иконки</SelectLabel>
          <SelectItem
            v-for="(icon, key) in STOP_MARKER_ICONS"
            :key="key"
            :value="key"
          >
            {{ icon.nameRu }}
          </SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  </div>
</template>
