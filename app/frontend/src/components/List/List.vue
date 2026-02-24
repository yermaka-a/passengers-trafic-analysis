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

import { Toggle } from "@/components/ui/toggle/";
import { Button } from "@/components/ui/button";
import { useMapStore } from "@/store";
import L from "leaflet";
const mapObjectStore = useMapObjectStore();
const { Objects } = storeToRefs(mapObjectStore);
const mapStore = useMapStore();
const { mapInstance } = storeToRefs(mapStore);
const changeColor = (e: MouseEvent, Id: string) => {
  const target = e.target as HTMLInputElement;

  const obj = Objects.value.get(Id);
  if (obj) {
    obj.setStyle({ color: target.value });
  }
};
const toggleStroke = (Id: string) => {
  const obj = Objects.value.get(Id);
  if (obj) {
    const isStroke = obj.options.stroke;
    obj.setStyle({ stroke: !isStroke });
  }
};
const changeDash = (value: number[] | undefined, Id: string) => {
  const obj = Objects.value.get(Id);
  if (obj && value) {
    obj.setStyle({ dashArray: value });
  }
};

const changeFillOpacity = (value: number[] | undefined, Id: string) => {
  const obj = Objects.value.get(Id);
  if (obj && value) {
    console.log(value);
    obj.setStyle({ fillOpacity: value[0] });
  }
};
const changeWeight = (value: number[] | undefined, Id: string) => {
  const obj = Objects.value.get(Id);
  if (obj && value) {
    obj.setStyle({ weight: value[0] });
  }
};
const toggleFill = (Id: string) => {
  const obj = Objects.value.get(Id);
  if (obj) {
    const isFill = obj.options.fill;
    obj.setStyle({ fill: !isFill });
  }
};
const deleteObject = (Id: string) => {
  const obj = Objects.value.get(Id);
  if (obj) {
    obj.remove();
    Objects.value.delete(Id);
  }
};
const findOnMap = (Id: string) => {
  const obj = Objects.value.get(Id);
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
    <div class="flex gap-3 flex-wrap">
      <Card
        v-for="(obj, idx) in Objects.entries()"
        :key="obj[0]"
        class="relative mx-auto w-full max-w-sm pt-0 min-w-58"
      >
        <CardHeader class="pt-2 min-w-min">
          <CardAction class="relative">
            <Button
              variant="link"
              size="sm"
              class="cursor-pointer relative bottom-2"
              @click="deleteObject(obj[0])"
              >Удалить</Button
            >
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
                :model-value="obj[1].options.stroke"
                @click="findOnMap(obj[0])"
                size="default"
                variant="outline"
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
                    :defaultValue="[0.1]"
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
                    :defaultValue="[0]"
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
</template>

<style scoped>
.list {
  display: flex;
}
</style>
