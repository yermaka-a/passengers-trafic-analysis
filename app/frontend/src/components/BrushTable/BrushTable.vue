<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { ButtonGroup } from "@/components/ui/button-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { STOP_MARKER_ICONS, type StopMarkerType } from "@/config/stopMarkers";
import { ref, computed } from "vue";

const mapObjectStore = useMapObjectStore();

const selectedMarkerType = ref<StopMarkerType>('bus');

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
    <Select
      v-if="isStopMarkerSelected"
      :model-value="selectedMarkerType"
      @update:model-value="(value) => selectedMarkerType = value as StopMarkerType"
    >
      <SelectTrigger>
        <SelectValue placeholder="Выберите тип маркера" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem
          v-for="(icon, key) in STOP_MARKER_ICONS"
          :key="key"
          :value="key"
        >
          {{ icon.nameRu }}
        </SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
