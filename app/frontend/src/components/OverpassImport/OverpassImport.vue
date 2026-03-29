<script setup lang="ts">
import { ref } from "vue";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import useApi from "@/composables/useApi";

interface StopImportResult {
  status: "success" | "failed";
  imported_count: number;
  duplicate_count: number;
  message?: string;
}

interface Props {
  open: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  open: false,
});

const emit = defineEmits<{
  'update:open': [value: boolean];
  'imported': [];
}>();

const { importStopsFromOverpass } = useApi();

const loading = ref(false);
const cities = ref("Ангарск");
const stopTypes = ref(["bus_stop", "platform"]);

const handleImport = async () => {
  loading.value = true;
  try {
    const result = await importStopsFromOverpass(cities.value, stopTypes.value) as StopImportResult;
    
    if (result.status === "success") {
      console.log(`✅ Импортировано: ${result.imported_count}, дубликатов: ${result.duplicate_count}`);
      emit('imported');
      emit('update:open', false);
    } else {
      console.error("❌ Ошибка импорта:", result.message);
      alert(`Ошибка: ${result.message}`);
    }
  } catch (e) {
    console.error("Ошибка импорта:", e);
    alert(`Ошибка: ${e}`);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-[500px]">
      <DialogHeader>
        <DialogTitle>Импорт остановок из OpenStreetMap</DialogTitle>
      </DialogHeader>
      
      <div class="space-y-4 py-4">
        <div class="space-y-2">
          <Label for="cities">Города (через запятую)</Label>
          <Textarea
            id="cities"
            v-model="cities"
            placeholder="Ангарск, Москва, Санкт-Петербург"
            class="min-h-[80px]"
          />
          <p class="text-xs text-muted-foreground">
            Введите названия городов как они указаны в OpenStreetMap
          </p>
        </div>
        
        <div class="space-y-2">
          <Label>Типы остановок</Label>
          <div class="grid grid-cols-2 gap-3">
            <div class="flex items-center space-x-2">
              <input
                type="checkbox"
                id="bus_stop"
                value="bus_stop"
                v-model="stopTypes"
                class="h-4 w-4"
              />
              <Label for="bus_stop" class="text-sm font-normal cursor-pointer">
                🚌 Автобусы
              </Label>
            </div>
            <div class="flex items-center space-x-2">
              <input
                type="checkbox"
                id="platform"
                value="platform"
                v-model="stopTypes"
                class="h-4 w-4"
              />
              <Label for="platform" class="text-sm font-normal cursor-pointer">
                🚉 Платформы
              </Label>
            </div>
            <div class="flex items-center space-x-2">
              <input
                type="checkbox"
                id="tram_stop"
                value="tram_stop"
                v-model="stopTypes"
                class="h-4 w-4"
              />
              <Label for="tram_stop" class="text-sm font-normal cursor-pointer">
                🚊 Трамваи
              </Label>
            </div>
            <div class="flex items-center space-x-2">
              <input
                type="checkbox"
                id="train_station"
                value="train_station"
                v-model="stopTypes"
                class="h-4 w-4"
              />
              <Label for="train_station" class="text-sm font-normal cursor-pointer">
                🚆 Ж/д станции
              </Label>
            </div>
          </div>
        </div>
      </div>
      
      <div class="flex justify-end gap-2">
        <Button variant="outline" @click="emit('update:open', false)" :disabled="loading">
          Отмена
        </Button>
        <Button @click="handleImport" :disabled="loading">
          <span v-if="loading" class="flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Импорт...
          </span>
          <span v-else>🚏 Импортировать</span>
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>
