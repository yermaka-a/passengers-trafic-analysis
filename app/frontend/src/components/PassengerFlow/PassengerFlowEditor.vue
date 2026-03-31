<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useMapObjectStore } from "@/store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Plus, Trash2, Save, X, Check, ChevronsUpDown } from "lucide-vue-next";

const mapObjectStore = useMapObjectStore();

const open = defineModel<boolean>("open", { default: false });
const emit = defineEmits<{
  saved: [];
}>();

// Форма создания/редактирования
const flowId = ref<string | null>(null);
const flowName = ref("");
const flowDate = ref(new Date().toISOString().split("T")[0]);
const flowDirection = ref("forward");
const flowDescription = ref("");
const flowRouteId = ref<string | null>(null);

// Остановки в потоке
interface FlowStop {
  stop_id: string;
  stop_name: string;
  order: number;
  passengers_on_board: number;
  passengers_off_board: number;
  passengers_remaining: number;
}

const flowStops = ref<FlowStop[]>([]);
const openCombobox = ref<string | null>(null);
const searchQueries = ref<Record<number, string>>({});
const searchInputRefs = ref<Record<number, HTMLInputElement | null>>({});

// Все остановки для выбора (отдельно для каждого индекса)
const getAvailableStops = (index: number) => {
  const allObjects = Array.from(mapObjectStore.Objects.entries());
  let stops = allObjects
    .filter(([_, obj]) => obj.type === "StopMarker")
    .map(([id, obj]) => ({
      id,
      name: obj.customName || obj.name || "Без названия"
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

  // Фильтруем по поиску для этого индекса
  const query = (searchQueries.value[index] || "").toLowerCase();
  if (query) {
    stops = stops.filter(stop => stop.name.toLowerCase().includes(query));
  }

  // Исключаем уже выбранные остановки
  const selectedIds = flowStops.value
    .filter((_, i) => i !== index)
    .map(s => s.stop_id);
  
  return stops.filter(s => !selectedIds.includes(s.id));
};

// Добавить остановку
const addStop = () => {
  const nextOrder = flowStops.value.length > 0 
    ? Math.max(...flowStops.value.map(s => s.order)) + 1 
    : 1;
  
  flowStops.value.push({
    stop_id: "",
    stop_name: "",
    order: nextOrder,
    passengers_on_board: 0,
    passengers_off_board: 0,
    passengers_remaining: 0
  });
};

// Удалить остановку
const removeStop = (index: number) => {
  flowStops.value.splice(index, 1);
  // Пересчитываем порядок
  flowStops.value.forEach((stop, idx) => {
    stop.order = idx + 1;
  });
};

// Выбрать остановку из списка
const selectStop = (index: number, stopId: string) => {
  const stop = getAvailableStops(index).find(s => s.id === stopId);
  if (stop && flowStops.value[index]) {
    flowStops.value[index].stop_id = stopId;
    flowStops.value[index].stop_name = stop.name;
    openCombobox.value = null;
    searchQueries.value[index] = "";
  }
};

// Обработка ввода поиска с debounce
const handleSearchInput = (index: number, value: string) => {
  searchQueries.value[index] = value;
};

// Обработка открытия/закрытия combobox
const handleComboboxOpen = (index: number, val: boolean) => {
  if (!val) {
    openCombobox.value = null;
    searchQueries.value[index] = "";
  } else {
    openCombobox.value = `stop-${index}`;
    // Фокус на input после открытия
    setTimeout(() => {
      if (searchInputRefs.value[index]) {
        searchInputRefs.value[index]?.focus();
      }
    }, 100);
  }
};

// Пересчитать остаток пассажиров
const recalculateRemaining = () => {
  let remaining = 0;
  flowStops.value.forEach(stop => {
    remaining = remaining + stop.passengers_on_board - stop.passengers_off_board;
    stop.passengers_remaining = Math.max(0, remaining);
  });
};

// Сохранить поток
const saveFlow = async () => {
  try {
    const { create_passenger_flow, update_passenger_flow } = (window as any).pywebview?.api || {};
    
    if (!create_passenger_flow) {
      alert("❌ API недоступно");
      return;
    }
    
    const stopsData = flowStops.value.map(stop => ({
      stop_id: stop.stop_id,
      order: stop.order,
      passengers_on_board: stop.passengers_on_board,
      passengers_off_board: stop.passengers_off_board
    }));
    
    const data = {
      name: flowName.value,
      date: flowDate.value,
      direction: flowDirection.value,
      description: flowDescription.value,
      route_id: flowRouteId.value || undefined,
      stops: stopsData
    };
    
    let result;
    if (flowId.value) {
      result = await update_passenger_flow({
        flow_id: flowId.value,
        ...data
      });
    } else {
      result = await create_passenger_flow(data);
    }
    
    if (result?.status === "success") {
      alert("✅ Пассажиропоток сохранён");
      emit("saved");
      open.value = false;
      resetForm();
    } else {
      alert(`❌ Ошибка: ${result?.message}`);
    }
  } catch (e) {
    console.error("saveFlow error:", e);
    alert(`❌ Ошибка: ${e}`);
  }
};

// Сброс формы
const resetForm = () => {
  flowId.value = null;
  flowName.value = "";
  flowDate.value = new Date().toISOString().split("T")[0];
  flowDirection.value = "forward";
  flowDescription.value = "";
  flowRouteId.value = null;
  flowStops.value = [];
};

// Открыть для редактирования
const openForEdit = async (flow: any) => {
  resetForm();
  flowId.value = flow.flow_id;
  flowName.value = flow.name;
  flowDate.value = flow.date;
  flowDirection.value = flow.direction;
  flowDescription.value = flow.description || "";
  flowRouteId.value = flow.route_id || null;
  
  if (flow.stops) {
    flowStops.value = flow.stops.map((stop: any) => ({
      stop_id: stop.stop_id,
      stop_name: stop.stop_name,
      order: stop.stop_order,
      passengers_on_board: stop.passengers_on_board,
      passengers_off_board: stop.passengers_off_board,
      passengers_remaining: stop.passengers_remaining
    }));
  }
  
  open.value = true;
};

// Отслеживаем изменения для пересчёта
watch(flowStops, () => {
  recalculateRemaining();
}, { deep: true });

// Экспортируем для внешнего использования
defineExpose({ openForEdit, resetForm });
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="max-w-none w-[95vw] max-h-[90vh] p-0 flex flex-col overflow-hidden">
      <DialogHeader class="px-6 py-4 border-b">
        <DialogTitle>
          {{ flowId ? "Редактировать пассажиропоток" : "Новый пассажиропоток" }}
        </DialogTitle>
      </DialogHeader>

      <div class="flex-1 overflow-auto px-6 py-4">
        <!-- Основная информация -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="space-y-2">
            <Label>Название *</Label>
            <Input v-model="flowName" placeholder="Например: Маршрут №5 - Утренний" />
          </div>

          <div class="space-y-2">
            <Label>Дата *</Label>
            <Input v-model="flowDate" type="date" />
          </div>

          <div class="space-y-2">
            <Label>Направление</Label>
            <Select v-model="flowDirection">
              <SelectTrigger>
                <SelectValue placeholder="Выберите направление" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="forward">Прямое (→)</SelectItem>
                <SelectItem value="backward">Обратное (←)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2 col-span-2">
            <Label>Описание</Label>
            <Input v-model="flowDescription" placeholder="Описание пассажиропотока" />
          </div>
        </div>

        <!-- Остановки -->
        <div class="border rounded-lg">
          <div class="flex items-center justify-between p-3 border-b bg-muted/50">
            <h3 class="font-semibold">Остановки в потоке</h3>
            <Button @click="addStop" size="sm" variant="outline">
              <Plus class="w-4 h-4 mr-2" />
              Добавить остановку
            </Button>
          </div>

          <div class="divide-y max-h-[400px] overflow-auto">
            <div
              v-for="(stop, index) in flowStops"
              :key="index"
              class="flex items-center gap-2 p-3 hover:bg-muted/50"
            >
              <!-- Порядок -->
              <div class="w-12 text-center font-bold text-lg">
                {{ stop.order }}
              </div>
              
              <!-- Выбор остановки -->
              <div class="flex-1">
                <Popover :open="openCombobox === `stop-${index}`" @update:open="handleComboboxOpen(index, $event)">
                  <PopoverTrigger as-child>
                    <Button
                      variant="outline"
                      role="combobox"
                      :aria-expanded="openCombobox === `stop-${index}`"
                      class="w-full justify-between"
                    >
                      <span class="truncate">
                        {{ stop.stop_name || "Выберите остановку" }}
                      </span>
                      <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent class="w-[350px] p-0" align="start">
                    <Command should-filter-string v-model:search-query="searchQueries[index]">
                      <CommandInput
                        ref="el => searchInputRefs[index] = el"
                        placeholder="Поиск остановки..."
                        @update:model-value="handleSearchInput(index, $event)"
                      />
                      <CommandList>
                        <CommandEmpty v-if="searchQueries[index]?.length > 0">
                          Ничего не найдено
                        </CommandEmpty>
                        <CommandEmpty v-else>
                          Начните вводить название
                        </CommandEmpty>
                        <CommandGroup>
                          <CommandItem
                            v-for="s in getAvailableStops(index)"
                            :key="s.id"
                            :value="s.id"
                            @select="selectStop(index, s.id)"
                          >
                            <Check
                              :class="stop.stop_id === s.id ? 'opacity-100' : 'opacity-0'"
                              class="mr-2 h-4 w-4"
                            />
                            {{ s.name }}
                          </CommandItem>
                        </CommandGroup>
                      </CommandList>
                    </Command>
                  </PopoverContent>
                </Popover>
              </div>
              
              <!-- Село -->
              <div class="w-24">
                <Input
                  v-model.number="stop.passengers_on_board"
                  type="number"
                  min="0"
                  placeholder="Село"
                  class="text-center"
                />
              </div>
              
              <!-- Вышло -->
              <div class="w-24">
                <Input
                  v-model.number="stop.passengers_off_board"
                  type="number"
                  min="0"
                  placeholder="Вышло"
                  class="text-center"
                />
              </div>
              
              <!-- Остаток (авто) -->
              <div class="w-24 text-center font-medium text-muted-foreground">
                {{ stop.passengers_remaining }}
              </div>
              
              <!-- Удалить -->
              <Button
                @click="removeStop(index)"
                size="icon"
                variant="ghost"
                class="text-destructive hover:text-destructive"
              >
                <Trash2 class="w-4 h-4" />
              </Button>
            </div>

            <div v-if="flowStops.length === 0" class="p-8 text-center text-muted-foreground">
              Нет остановок. Нажмите "Добавить остановку"
            </div>
          </div>

          <!-- Итого -->
          <div class="p-3 border-t bg-muted/30">
            <div class="flex justify-between text-sm">
              <span>Всего остановок:</span>
              <span class="font-bold">{{ flowStops.length }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span>Всего село:</span>
              <span class="font-bold">{{ flowStops.reduce((sum, s) => sum + s.passengers_on_board, 0) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span>Всего вышло:</span>
              <span class="font-bold">{{ flowStops.reduce((sum, s) => sum + s.passengers_off_board, 0) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Кнопки -->
      <div class="flex justify-end gap-2 px-6 py-4 border-t">
        <Button @click="open = false; resetForm()" variant="outline">
          <X class="w-4 h-4 mr-2" />
          Отмена
        </Button>
        <Button @click="saveFlow">
          <Save class="w-4 h-4 mr-2" />
          Сохранить
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>
