<script setup lang="ts">
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { storeToRefs } from "pinia";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionTrigger,
  AccordionItem,
} from "@/components/ui/accordion";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardContent,
  CardTitle,
} from "@/components/ui/card";
import { AlertCircleIcon } from "lucide-vue-next";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Toggle } from "@/components/ui/toggle/";
import { Button } from "@/components/ui/button";
import { useMapStore } from "@/store";
import { useApi } from "@/composables";
import { Spinner } from "@/components/ui/spinner";
import { ref, Teleport } from "vue";
import type { DeckGLObject } from "@/types";
import { rgbaToHex, hexToRGBA } from "@/utils";

const mapObjectStore = useMapObjectStore();
const { Objects } = storeToRefs(mapObjectStore);
const mapStore = useMapStore();

const closeModalRef = ref(false);
const onCloseModal = () => {
  closeModalRef.value = false;
  console.error(deletingError);
  console.error(updateError);
};

const { deleteObject, loading, error: deletingError } = useApi();
const { updateObject, error: updateError } = useApi();

const changeColor = async (e: MouseEvent, id: string) => {
  const target = e.target as HTMLInputElement;
  if (!target.value) return; // Защита от пустого цвета
  const newColor = hexToRGBA(target.value);
  mapObjectStore.updateObjectStyle(id, { color: newColor });

  // Берём обновлённый объект из store
  const updatedObj = mapObjectStore.getObjectById(id);
  if (updatedObj) {
    await updateObjectInBackend(updatedObj);
  }
};

const toggleStroke = async (id: string) => {
  const obj = Objects.value?.get(id);
  if (obj) {
    // Переключаем только видимость обводки
    // strokeState хранит фактические значения и будет восстановлен при включении
    const hide = obj.style.strokeWidth > 0;
    mapObjectStore.toggleStrokeVisibility(id, hide);
    const updatedObj = mapObjectStore.getObjectById(id);
    if (updatedObj) await updateObjectInBackend(updatedObj);
  }
};

const changeDash = async (value: number[], id: string) => {
  const obj = Objects.value?.get(id);
  if (obj && value) {
    // [длина_штриха, длина_пробела] - пробел равен половине штриха
    const dashValue =
      value[0] === 0 ? [0, 0] : ([value[0], value[0] / 2] as [number, number]);
    mapObjectStore.updateObjectStyle(id, {
      strokeDasharray: dashValue,
    });
    const updatedObj = mapObjectStore.getObjectById(id);
    if (updatedObj) await updateObjectInBackend(updatedObj);
  }
};

const changeFillOpacity = async (value: number[], id: string) => {
  const obj = Objects.value?.get(id);
  if (obj && value) {
    mapObjectStore.updateObjectStyle(id, { fillOpacity: value[0] });
    const updatedObj = mapObjectStore.getObjectById(id);
    if (updatedObj) await updateObjectInBackend(updatedObj);
  }
};

const changeWeight = async (value: number[], id: string) => {
  const obj = Objects.value?.get(id);
  if (obj && value) {
    mapObjectStore.updateObjectStyle(id, { strokeWidth: value[0] });
    const updatedObj = mapObjectStore.getObjectById(id);
    if (updatedObj) await updateObjectInBackend(updatedObj);
  }
};

const toggleFill = async (id: string) => {
  const obj = Objects.value?.get(id);
  if (obj) {
    mapObjectStore.updateObjectStyle(id, { filled: !obj.style.filled });
    const updatedObj = mapObjectStore.getObjectById(id);
    if (updatedObj) await updateObjectInBackend(updatedObj);
  }
};

// Обновление объекта в бэкенде
const updateObjectInBackend = async (obj: DeckGLObject) => {
  const backendObj = mapObjectStore.convertDeckGLToBackend(obj);
  const result = await updateObject(backendObj);

  // Проверяем успешность обновления
  if (result?.status !== "success") {
    console.error("[List] Ошибка обновления:", result);
  }
};

const delObject = async (id: string) => {
  const success = await deleteObject(id);
  if (success) {
    mapObjectStore.deleteObject(id);
  }
};

const findOnMap = (id: string) => {
  const obj = Objects.value?.get(id);
  if (obj && obj.coordinates.length > 0) {
    const coord = obj.coordinates[0];
    if (coord) {
      const [lng, lat] = coord;
      mapStore.updateViewState({ latitude: lat, longitude: lng, zoom: 16 });
    }
  }
};

// ============================================================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ============================================================================

// Получение координат для отображения
const getCoordinates = (obj: DeckGLObject) => {
  return obj.coordinates.map(([lng, lat]) => ({ lat, lng }));
};

// Конвертация dashArray для слайдера
const getDashValue = (obj: DeckGLObject): number[] => {
  if (!obj.style.strokeDasharray) return [0];
  return [obj.style.strokeDasharray[0] ?? 0];
};
</script>

<template>
  <div class="px-8 h-dvh overflow-scroll pb-60">
    <h2
      class="scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight transition-colors first:mt-0 mb-4"
    >
      Настройки
    </h2>
    <div v-if="Objects && Objects.size > 0" class="flex gap-3 flex-wrap">
      <Card
        v-for="(obj, idx) in Objects.entries()"
        :key="obj[0]"
        class="relative mx-auto w-full max-w-sm pt-0 min-w-58"
      >
        <CardHeader class="pt-2 min-w-min">
          <CardAction class="relative">
            <Button
              v-if="!loading"
              variant="link"
              size="sm"
              class="cursor-pointer relative bottom-2"
              @click="delObject(obj[0])"
              >Удалить</Button
            >
            <Badge v-else variant="secondary">
              <Spinner />
              Удаление
            </Badge>
          </CardAction>
          <CardTitle class="min-w-min">{{ obj[1].name }}</CardTitle>
        </CardHeader>
        <CardContent>
          <CardDescription>
            <Accordion
              v-if="obj[1].type === 'Polygon' || obj[1].type === 'Polyline'"
              type="single"
              collapsible
            >
              <AccordionItem value="item-1">
                <AccordionTrigger class="mb-4 text-sm leading-none font-medium">
                  широта:долгота
                </AccordionTrigger>
                <AccordionContent>
                  <template
                    v-for="coord in getCoordinates(obj[1])"
                    :key="`${coord.lat}-${coord.lng}`"
                  >
                    {{ coord.lat }} : {{ coord.lng }}
                    <Separator class="my-2" />
                  </template>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
            <template v-else-if="obj[1].type === 'CircleMarker'">
              <Accordion type="single" collapsible>
                <AccordionItem value="item-1">
                  <AccordionTrigger
                    class="mb-4 text-sm leading-none font-medium"
                  >
                    широта:долгота
                  </AccordionTrigger>
                  <AccordionContent>
                    <template v-if="obj[1].coordinates.length > 0">
                      {{
                        `${obj[1].coordinates[0]?.[1] ?? 0} : ${obj[1].coordinates[0]?.[0] ?? 0}`
                      }}
                    </template>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </template>
            <div class="flex flex-wrap items-center gap-1">
              <Input
                @input="changeColor($event, obj[0])"
                class="w-1/4 min-w-16"
                type="color"
                :model-value="rgbaToHex(obj[1].style.color)"
              />

              <Toggle
                :model-value="obj[1].style.strokeWidth > 0"
                @click="toggleStroke(obj[0])"
                size="default"
                variant="outline"
                >Обводка</Toggle
              >
              <Toggle
                @click="findOnMap(obj[0])"
                size="default"
                variant="outline"
                :model-value="false"
                >На карте</Toggle
              >
              <Separator class="my-2 w-40" />
              <div>
                <small className="text-sm leading-none font-medium"
                  >Пунктир</small
                >
                <Slider
                  @update:model-value="
                    (value) => {
                      if (value) changeDash(value, obj[0]);
                    }
                  "
                  :model-value="getDashValue(obj[1])"
                  :max="100"
                  :step="1"
                  :min="0"
                  class="mx-auto w-40 max-w-xs"
                />
              </div>
              <Separator class="my-2 w-40" />
              <div>
                <div class="flex items-center gap-1">
                  <small class="text-sm leading-none font-medium"
                    >Заливка</small
                  >
                  <Checkbox
                    class="size-5"
                    :model-value="obj[1].style.filled"
                    @click="toggleFill(obj[0])"
                  />
                </div>
                <div class="flex gap-3 flex-wrap pb-2">
                  <small class="text-sm leading-none font-medium"
                    >Прозрачность заливки</small
                  >
                  <Slider
                    @update:model-value="
                      (value) => {
                        if (value) changeFillOpacity(value, obj[0]);
                      }
                    "
                    :disabled="!obj[1].style.filled"
                    :model-value="[obj[1].style.fillOpacity ?? 0.5]"
                    :max="1"
                    :step="0.01"
                    :min="0"
                    class="mx-auto w-full max-w-xs"
                  />
                </div>
                <div class="flex gap-3 flex-wrap">
                  <small class="text-sm leading-none font-medium"
                    >Жирность обводки</small
                  >
                  <Slider
                    @update:model-value="
                      (value) => {
                        if (value) changeWeight(value, obj[0]);
                      }
                    "
                    :model-value="[obj[1].style.strokeWidth ?? 2]"
                    :max="200"
                    :step="1"
                    :min="0"
                    class="mx-auto w-full max-w-xs"
                  />
                </div>
              </div>
            </div>
          </CardDescription>
        </CardContent>
        <CardFooter class="flex justify-end">
          <Badge variant="secondary">№ {{ idx + 1 }}</Badge>
        </CardFooter>
      </Card>
    </div>
    <div v-else class="text-center text-gray-500 mt-10">
      Нет созданных объектов
    </div>
  </div>
  <Teleport v-if="closeModalRef" to="body">
    <div class="fixed bg-black/40 inset-0 z-400" @click="onCloseModal">
      <Alert
        variant="destructive"
        class="max-w-fit p-5 z-500 fixed top-[50%] left-[45%]"
      >
        <AlertCircleIcon />
        <AlertTitle>Произошла ошибка</AlertTitle>
        <AlertDescription>
          <p v-if="deletingError">Неудачное удаление</p>
          <p v-if="updateError">Неудачное обновление</p>
        </AlertDescription>
      </Alert>
    </div>
  </Teleport>
</template>

<style scoped>
.list {
  display: flex;
}
</style>
