<script setup lang="ts">
import { Plus, X, ChevronLeft, ChevronRight } from "lucide-vue-next";
import { Button } from "@/components/ui/button";
interface Props {
  cancelChanges: () => void;
  submitChanges: () => void;
  prevAction: () => void;
  nextAction: () => void;
}
const props = defineProps<Props>();
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
    @click="prevAction()"
  >
    <ChevronLeft />
  </Button>
  <Button
    class="cursor-pointer"
    variant="outline"
    size="icon"
    @click="nextAction()"
  >
    <ChevronRight />
  </Button>
</template>
