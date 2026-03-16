<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { ButtonGroup } from "@/components/ui/button-group";
import { useMapObjectStore } from "@/store/useMapObjectStore";

const mapObjectStore = useMapObjectStore();

const isActive = (option: (typeof mapObjectStore.getObjectsTypes)[number]) => {
  return option[1] === mapObjectStore.getChosenObjectType[1];
};
</script>

<template>
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
      {{ option[1] }}</Button
    >
  </ButtonGroup>
</template>
