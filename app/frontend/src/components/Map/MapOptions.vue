<script setup lang="ts">
import { Plus, X, ChevronLeft, ChevronRight } from "lucide-vue-next";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";

interface Props {
  cancelChanges: () => void;
  submitChanges: () => void;
  prevAction: () => void;
  nextAction: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
  draftColor?: string;
  showCoordinates?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  canUndo: false,
  canRedo: false,
  draftColor: "#ff0000",
  showCoordinates: true,
});

const emit = defineEmits<{
  "update:draftColor": [value: string];
  "update:showCoordinates": [value: boolean];
}>();

const handleSubmit = () => {
  console.log("[MapOptions] submitChanges вызван");
  props.submitChanges();
};

const handleCancel = () => {
  console.log("[MapOptions] cancelChanges вызван");
  props.cancelChanges();
};

const handleColorChange = (value: string) => {
  emit("update:draftColor", value);
};
</script>

<template>
  <div class="flex items-center gap-2">
    <Button
      class="cursor-pointer"
      variant="outline"
      size="sm"
      @click="handleSubmit()"
    >
      <Plus />Добавить</Button
    >
    <Button
      class="cursor-pointer"
      variant="outline"
      size="sm"
      @click="handleCancel()"
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
    <Separator orientation="vertical" class="h-6" />
    <Button
      variant="outline"
      size="sm"
      :class="props.showCoordinates ? 'bg-accent' : ''"
      @click="emit('update:showCoordinates', !props.showCoordinates)"
      title="Показать координаты"
    >
      <span class="text-xs font-mono">GPS</span>
    </Button>
    <Input
      v-if="draftColor !== undefined"
      type="color"
      :model-value="draftColor"
      @update:model-value="handleColorChange"
      class="w-10 h-9 p-1 cursor-pointer"
    />
  </div>
</template>
