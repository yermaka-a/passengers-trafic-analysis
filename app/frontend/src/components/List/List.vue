<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ObjectListView, PropertyTable } from "@/components/ObjectList";
import { Button } from "@/components/ui/button";
import { LayoutGrid, Table as TableIcon } from "lucide-vue-next";

type ViewType = "cards" | "table";

const view = ref<ViewType>("cards");

// Загружаем предпочтения из localStorage
onMounted(() => {
  const savedView = localStorage.getItem("objectListView") as ViewType;
  if (savedView === "cards" || savedView === "table") {
    view.value = savedView;
  }
});

// Сохраняем выбор в localStorage
const setView = (newView: ViewType) => {
  view.value = newView;
  localStorage.setItem("objectListView", newView);
};
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Переключатель вида -->
    <div class="flex items-center justify-between px-8 py-4 border-b">
      <h1 class="text-2xl font-semibold">Объекты на карте</h1>
      <div class="flex items-center gap-2">
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
      <component :is="view === 'cards' ? ObjectListView : PropertyTable" :key="view" />
    </div>
  </div>
</template>

<style scoped>
/* Анимация переключения */
.view-transition {
  transition: opacity 0.2s ease-in-out;
}
</style>
