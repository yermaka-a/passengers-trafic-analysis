<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useMapObjectStore } from "@/store/useMapObjectStore";
import { Input } from "@/components/ui/input";
import type { DeckGLObject } from "@/types";

const props = defineProps<{
  objects: [string, DeckGLObject][];
}>();

const mapObjectStore = useMapObjectStore();

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
    const backendObj = mapObjectStore.convertDeckGLToBackend(updatedObj);
    const { updateObject } = useApi();
    await updateObject(backendObj);
  }
};

const updateDescription = async (id: string, value: string) => {
  const obj = mapObjectStore.Objects.get(id);
  if (obj) {
    const updatedObj = { ...obj, description: value || null };
    mapObjectStore.Objects.set(id, updatedObj);
    const backendObj = mapObjectStore.convertDeckGLToBackend(updatedObj);
    const { updateObject } = useApi();
    await updateObject(backendObj);
  }
};

const closeModalRef = ref(false);
const deletingError = ref(false);
const updateError = ref(false);

const onCloseModal = () => {
  closeModalRef.value = false;
  console.error(deletingError);
  console.error(updateError);
};
</script>

<template>
  <div class="px-8 h-dvh overflow-scroll pb-60">
    <div v-if="props.objects && props.objects.length > 0" class="flex gap-3 flex-wrap">
      <Card
        v-for="(obj, idx) in props.objects"
        :key="obj[0]"
        class="relative mx-auto w-full max-w-sm pt-0 min-w-58"
      >
        <CardHeader class="pt-2 min-w-min">
          <CardAction class="relative">
            <Button
              v-if="!deletingError"
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
          <CardTitle class="min-w-min">
            <div class="flex flex-col gap-1">
              <span>{{ obj[1].customName || obj[1].name }}</span>
              <span v-if="obj[1].description" class="text-xs text-gray-500">{{ obj[1].description }}</span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <CardDescription>
            <!-- Редактирование customName и description -->
            <div class="flex gap-2 mb-4">
              <Input
                v-model="obj[1].customName"
                @change="(e) => updateCustomName(obj[0], (e.target as HTMLInputElement).value)"
                placeholder="Название"
                class="flex-1"
              />
            </div>
            <textarea
              v-model="obj[1].description"
              @change="(e) => updateDescription(obj[0], (e.target as HTMLTextAreaElement).value)"
              placeholder="Описание"
              class="w-full border rounded-md px-3 py-2 text-sm mb-4 resize-none"
              rows="2"
            />
            
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
                @update:model-value="(value) => changeColor(value, obj[0])"
                class="w-1/4 min-w-16"
                type="color"
                :model-value="
                  rgbaToHex(
                    obj[1].style.color ?? [0, 128, 255, 255],
                  )
                "
              />

              <Toggle
                :model-value="(obj[1].style.strokeWidth ?? 0) > 0"
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
              <Separator class="my-2 w-full" />
              <div v-if="obj[1].type !== 'CircleMarker'">
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
              <Separator class="my-2 w-full" />
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
                <div class="flex gap-3 flex-wrap" v-if="obj[1].type === 'CircleMarker'">
                  <small class="text-sm leading-none font-medium"
                    >Размер маркера</small
                  >
                  <Slider
                    @update:model-value="
                      (value) => {
                        if (value) changeRadius(value, obj[0]);
                      }
                    "
                    :model-value="[obj[1].style.radius ?? 10]"
                    :max="50"
                    :step="1"
                    :min="5"
                    class="mx-auto w-full max-w-xs"
                  />
                </div>
                <div class="flex gap-3 flex-wrap" v-if="obj[1].type !== 'CircleMarker'">
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
