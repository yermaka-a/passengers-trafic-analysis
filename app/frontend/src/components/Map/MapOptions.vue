<script setup lang="ts">
import { Plus, X, ChevronLeft, ChevronRight } from "lucide-vue-next";
import { Button } from "@/components/ui/button";

interface Props {
  cancelChanges: () => void;
  submitChanges: () => void;
  prevAction: () => void;
  nextAction: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  canUndo: false,
  canRedo: false,
});
</script>

<template>
  <Button
    class="cursor-pointer"
    variant="outline"
    size="sm"
    @click="submitChanges()"
  >
    <Plus />Добавить</Button
  >
  <Button
    class="cursor-pointer"
    variant="outline"
    size="sm"
    @click="cancelChanges()"
  >
    <X /> Отменить
  </Button>
  <Button
    class="cursor-pointer"
    variant="outline"
    size="icon"
    :disabled="!canUndo"
    @click="prevAction()"
  >
    <ChevronLeft />
  </Button>
  <Button
    class="cursor-pointer"
    variant="outline"
    size="icon"
    :disabled="!canRedo"
    @click="nextAction()"
  >
    <ChevronRight />
  </Button>
</template>
