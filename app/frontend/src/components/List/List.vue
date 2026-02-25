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
import L from "leaflet";
import { useApi } from "@/composables";
import { Spinner } from "@/components/ui/spinner";
import { ref, Teleport } from "vue";
const mapObjectStore = useMapObjectStore();
const { Objects } = storeToRefs(mapObjectStore);
const mapStore = useMapStore();
const { mapInstance } = storeToRefs(mapStore);
const closeModalRef = ref(false);
const onCloseModal = () => {
  closeModalRef.value = false;
  console.error(deletingError);
  console.error(updateError);
};
const { deleteObject, loading, error: deletingError } = useApi();
const { updateObject, error: updateError } = useApi();
const changeColor = async (e: MouseEvent, Id: string) => {
  const target = e.target as HTMLInputElement;
  const obj = Objects.value?.get(Id);
  if (obj) {
    obj.setStyle({ color: target.value });
    await updateObject(obj);
  }
};
const toggleStroke = async (Id: string) => {
  const obj = Objects.value?.get(Id);
  if (obj) {
    const isStroke = obj.options.stroke;
    obj.setStyle({ stroke: !isStroke });
    await updateObject(obj);
  }
};
const changeDash = async (value: number[] | undefined, Id: string) => {
  const obj = Objects.value?.get(Id);
  if (obj && value) {
    obj.setStyle({ dashArray: value });
    await updateObject(obj);
  }
};

const changeFillOpacity = async (value: number[] | undefined, Id: string) => {
  const obj = Objects.value?.get(Id);
  if (obj && value) {
    console.log(value);
    obj.setStyle({ fillOpacity: value[0] });
    await updateObject(obj);
  }
};
const changeWeight = async (value: number[] | undefined, Id: string) => {
  const obj = Objects.value?.get(Id);
  if (obj && value) {
    obj.setStyle({ weight: value[0] });
    await updateObject(obj);
  }
};
const toggleFill = async (Id: string) => {
  const obj = Objects.value?.get(Id);
  if (obj) {
    const isFill = obj.options.fill;
    obj.setStyle({ fill: !isFill });
    await updateObject(obj);
  }
};
const delObject = async (Id: string) => {
  const obj = Objects.value?.get(Id);
  if (obj) {
    if (await deleteObject(obj.options.Id)) {
      obj.remove();
      Objects.value?.delete(Id);
    }
  }
};
const findOnMap = (Id: string) => {
  const obj = Objects.value?.get(Id);
  if (obj) {
    if (obj instanceof L.Polygon || obj instanceof L.Polyline) {
      mapInstance.value?.flyToBounds(obj.getBounds());
    }
    if (obj instanceof L.CircleMarker) {
      mapInstance.value?.flyTo(obj.getLatLng());
    }
  }
};
</script>

<template>
  <div class="px-8 h-dvh overflow-scroll pb-60">
    <h2
      class="scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight transition-colors first:mt-0 mb-4"
    >
      Настройки
    </h2>
    <div v-if="Objects" class="flex gap-3 flex-wrap">
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
          <CardTitle class="min-w-min">{{ obj[1].options.name }}</CardTitle>
        </CardHeader>
        <CardContent>
          <CardDescription>
            <Accordion
              v-if="obj[1] instanceof L.Polygon || obj[1] instanceof L.Polyline"
              type="single"
              collapsible
            >
              <AccordionItem value="item-1">
                <AccordionTrigger class="mb-4 text-sm leading-none font-medium">
                  широта:долгота
                </AccordionTrigger>
                <AccordionContent>
                  <template
                    v-for="latlng in obj[1]
                      .getLatLngs()
                      .flat()
                      .map((el) => {
                        el = el as L.LatLng;
                        return el;
                      })"
                    :key="latlng.lat.toString() + latlng.lng.toString()"
                  >
                    {{ latlng.lat }} : {{ latlng.lng }}
                    <Separator class="my-2" />
                  </template>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
            <template v-else-if="obj[1] instanceof L.CircleMarker">
              <Accordion type="single" collapsible>
                <AccordionItem value="item-1">
                  <AccordionTrigger
                    class="mb-4 text-sm leading-none font-medium"
                  >
                    широта:долгота
                  </AccordionTrigger>
                  <AccordionContent>
                    {{
                      `${obj[1].getLatLng().lat} : ${obj[1].getLatLng().lng}`
                    }}
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </template>
            <div class="flex flex-wrap items-center gap-1">
              <Input
                @change="changeColor($event, obj[0])"
                class="w-1/4 min-w-16"
                type="color"
                :default-value="obj[1].options.color"
              />

              <Toggle
                :model-value="obj[1].options.stroke"
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
                  @update:model-value="(value) => changeDash(value, obj[0])"
                  :defaultValue="[0]"
                  :max="100"
                  :step="1"
                  :min="0"
                  :model-value="(obj[1].options.dashArray as number[]) || [0]"
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
                    :model-value="obj[1].options.fill"
                    @click="toggleFill(obj[0])"
                  />
                </div>
                <div class="flex gap-3 flex-wrap pb-2">
                  <small class="text-sm leading-none font-medium"
                    >Прозрачность заливки</small
                  >
                  <Slider
                    @update:model-value="
                      (value) => changeFillOpacity(value, obj[0])
                    "
                    :disabled="!obj[1].options.fill"
                    :model-value="
                      [obj[1].options.fillOpacity as unknown] as number[]
                    "
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
                    @update:model-value="(value) => changeWeight(value, obj[0])"
                    :model-value="[obj[1].options.weight as number]"
                    :max="30"
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
