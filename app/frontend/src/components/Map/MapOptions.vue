<script setup lang="ts">
import { Plus, X, ChevronLeft, ChevronRight } from "lucide-vue-next";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Props {
  cancelChanges: () => void;
  submitChanges: () => void;
  prevAction: () => void;
  nextAction: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
  draftColor?: string;
}

const props = withDefaults(defineProps<Props>(), {
  canUndo: false,
  canRedo: false,
  draftColor: "#ff0000",
});

const emit = defineEmits<{
  "update:draftColor": [value: string];
}>();

const handleSubmit = () => {
  console.log("[MapOptions] submitChanges вызван");
  props.submitChanges();
};

const handleCancel = () => {
  console.log("[MapOptions] cancelChanges вызван");
  props.cancelChanges();
};

const handleColorChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  emit("update:draftColor", target.value);
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
    <Input
      v-if="draftColor !== undefined"
      type="color"
      :model-value="draftColor"
      @update:model-value="handleColorChange"
      class="w-10 h-9 p-1 cursor-pointer"
    />
  </div>
</template>
