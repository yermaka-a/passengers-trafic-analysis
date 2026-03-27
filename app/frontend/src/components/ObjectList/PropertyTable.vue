<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Search, X } from "lucide-vue-next";
import type { DeckGLObject } from "@/types";
import { rgbaToHex } from "@/utils";
import useObjectActions from "@/composables/useObjectActions";
import { useApi } from "@/composables";

const mapObjectStore = useMapObjectStore();
const { Objects } = storeToRefs(mapObjectStore);

const {
  changeColor,
  toggleStroke,
  changeDash,
  changeFillOpacity,
  changeWeight,
  toggleFill,
  changeRadius,
  delObject,
  findOnMap,
  getCoordinates,
  getDashValue,
} = useObjectActions();

const updateCustomName = async (id: string, value: string) => {
  const obj = mapObjectStore.Objects.get(id);
  if (obj) {
    const updatedObj = { ...obj, customName: value || null };
    mapObjectStore.Objects.set(id, updatedObj);
    await updateObjectInBackend(updatedObj);
  }
};

const updateDescription = async (id: string, value: string) => {
  const obj = mapObjectStore.Objects.get(id);
  if (obj) {
    const updatedObj = { ...obj, description: value || null };
    mapObjectStore.Objects.set(id, updatedObj);
    await updateObjectInBackend(updatedObj);
  }
};

const updateObjectInBackend = async (obj: DeckGLObject) => {
  const backendObj = mapObjectStore.convertDeckGLToBackend(obj);
  const { updateObject } = useApi();
  const result = await updateObject(backendObj);
  if (result?.status !== "success") {
    console.error("[PropertyTable] Ошибка обновления:", result);
  }
};

// Форматирование координат для отображения
const formatCoordinates = (obj: DeckGLObject): string => {
  const coords = getCoordinates(obj);
  if (coords.length === 0) return "-";
  if (coords.length === 1) {
    return `${coords[0]!.lat.toFixed(3)}:${coords[0]!.lng.toFixed(3)}`;
  }
  return `${coords.length} точек`;
};

// Получение иконки цвета
const getColorBadge = (obj: DeckGLObject) => {
  const hex = rgbaToHex(obj.style.color ?? [0, 0, 0, 255]);
  return hex;
};
</script>

<template>
  <div class="px-8 h-dvh overflow-scroll pb-60">
    <div v-if="Objects && Objects.size > 0" class="w-full">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead class="w-[50px]">№</TableHead>
            <TableHead class="w-[100px]">Тип</TableHead>
            <TableHead>Имя</TableHead>
            <TableHead class="w-[150px]">Координаты</TableHead>
            <TableHead class="w-[80px]">Цвет</TableHead>
            <TableHead class="w-[80px]">Обводка</TableHead>
            <TableHead class="w-[100px]">Пунктир</TableHead>
            <TableHead class="w-[80px]">Заливка</TableHead>
            <TableHead class="w-[100px]">Прозрачность</TableHead>
            <TableHead class="w-[100px]">Размер</TableHead>
            <TableHead class="w-[150px]">Действия</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="(obj, idx) in Objects.entries()"
            :key="obj[0]"
            class="group"
          >
            <TableCell class="font-medium">{{ idx + 1 }}</TableCell>
            <TableCell>
              <Badge variant="outline">
                {{ obj[1].type === "Polygon" ? "Полигон" : obj[1].type === "Polyline" ? "Полилайн" : "Маркер" }}
              </Badge>
            </TableCell>
            <TableCell>
              <div class="flex flex-col gap-1">
                <input
                  v-if="obj[1].customName"
                  :value="obj[1].customName"
                  @change="(e) => updateCustomName(obj[0], (e.target as HTMLInputElement).value)"
                  class="text-sm font-medium border rounded px-2 py-1 w-full"
                  placeholder="Название"
                />
                <span v-else class="text-sm text-gray-500">{{ obj[1].name }}</span>
                <textarea
                  v-if="obj[1].description"
                  :value="obj[1].description"
                  @change="(e) => updateDescription(obj[0], (e.target as HTMLTextAreaElement).value)"
                  class="text-xs text-gray-400 border rounded px-2 py-1 w-full resize-none"
                  placeholder="Описание"
                  rows="2"
                />
              </div>
            </TableCell>
            <TableCell class="text-sm text-gray-500">
              {{ formatCoordinates(obj[1]) }}
            </TableCell>
            <TableCell>
              <Input
                @update:model-value="(value) => changeColor(value, obj[0])"
                type="color"
                :model-value="getColorBadge(obj[1])"
                class="w-8 h-8 p-0 border-0 cursor-pointer"
              />
            </TableCell>
            <TableCell>
              <Checkbox
                :model-value="(obj[1].style.strokeWidth ?? 0) > 0"
                @update:model-value="toggleStroke(obj[0])"
              />
            </TableCell>
            <TableCell>
              <Slider
                v-if="(obj[1].style.strokeWidth ?? 0) > 0"
                @update:model-value="
                  (value) => {
                    if (value) changeDash(value, obj[0]);
                  }
                "
                :model-value="getDashValue(obj[1])"
                :max="100"
                :step="1"
                :min="0"
                class="w-20"
              />
              <span v-else class="text-gray-400">-</span>
            </TableCell>
            <TableCell>
              <Checkbox
                :model-value="obj[1].style.filled ?? false"
                @update:model-value="toggleFill(obj[0])"
              />
            </TableCell>
            <TableCell>
              <Slider
                v-if="obj[1].style.filled"
                @update:model-value="
                  (value) => {
                    if (value) changeFillOpacity(value, obj[0]);
                  }
                "
                :model-value="[obj[1].style.fillOpacity ?? 0.5]"
                :max="1"
                :step="0.01"
                :min="0"
                class="w-20"
              />
              <span v-else class="text-gray-400">-</span>
            </TableCell>
            <TableCell>
              <Slider
                v-if="obj[1].type === 'CircleMarker'"
                @update:model-value="
                  (value) => {
                    if (value) changeRadius(value, obj[0]);
                  }
                "
                :model-value="[obj[1].style.radius ?? 10]"
                :max="50"
                :step="1"
                :min="5"
                class="w-20"
              />
              <span v-else class="text-gray-400">-</span>
            </TableCell>
            <TableCell>
              <div class="flex gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  @click="findOnMap(obj[0])"
                  title="Найти на карте"
                  class="h-8 w-8 p-0"
                >
                  <Search class="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  @click="delObject(obj[0])"
                  class="h-8 w-8 p-0 text-red-500 hover:text-red-700"
                  title="Удалить"
                >
                  <X class="w-4 h-4" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <div v-else class="text-center text-gray-500 mt-10">
      Нет созданных объектов
    </div>
  </div>
</template>

<style scoped>
/* Убираем hover эффект для строк с input type=color */
:deep(tbody tr:hover input[type="color"]) {
  background: transparent;
}

/* Компактные слайдеры */
:deep([role="slider"]) {
  height: 4px;
}
</style>
