<script setup lang="ts">
import { useMapObjectStore } from "@/store/useMapObjectStore";
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
import { Spinner } from "@/components/ui/spinner";
import { Textarea } from "@/components/ui/textarea";
import { Pencil } from "lucide-vue-next";
import { ref, Teleport } from "vue";
import type { DeckGLObject } from "@/types";
import useObjectActions from "@/composables/useObjectActions";
import { useApi } from "@/composables";
import { rgbaToHex } from "@/utils";

const props = defineProps<{
  objects: [string, DeckGLObject][];
}>();

const mapObjectStore = useMapObjectStore();

const editingId = ref<string | null>(null);
const editingCustomName = ref<string>("");
const editingDescription = ref<string>("");
const expandedDescriptions = ref<Set<string>>(new Set());

const startEditing = (id: string, obj: DeckGLObject) => {
  editingId.value = id;
  editingCustomName.value = obj.customName || "";
  editingDescription.value = obj.description || "";
};

const cancelEditing = () => {
  editingId.value = null;
  editingCustomName.value = "";
  editingDescription.value = "";
};

const saveEditing = async (id: string) => {
  const obj = mapObjectStore.Objects.get(id);
  if (obj) {
    const updatedObj = {
      ...obj,
      customName: editingCustomName.value || null,
      description: editingDescription.value || null,
    };
    mapObjectStore.Objects.set(id, updatedObj);
    await updateObjectInBackend(updatedObj);
  }
  cancelEditing();
};

const toggleDescription = (id: string) => {
  if (expandedDescriptions.value.has(id)) {
    expandedDescriptions.value.delete(id);
  } else {
    expandedDescriptions.value.add(id);
  }
  // Force reactivity
  expandedDescriptions.value = new Set(expandedDescriptions.value);
};

const isExpanded = (id: string) => expandedDescriptions.value.has(id);

const truncateText = (text: string | null | undefined, maxLength: number = 10) => {
  if (!text) return "";
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "...";
};

const updateObjectInBackend = async (obj: DeckGLObject) => {
  const backendObj = mapObjectStore.convertDeckGLToBackend(obj);
  const { updateObject } = useApi();
  const result = await updateObject(backendObj);
  if (result?.status !== "success") {
    console.error("[ObjectListView] Ошибка обновления:", result);
  }
};

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

// Эмит для открытия popup в Map.vue
const emit = defineEmits<{
  openPopup: [id: string];
}>();

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
  <div class="px-8 h-full overflow-y-auto pb-60">
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
            <div class="flex items-center gap-2">
              <span class="flex-1 truncate" :title="obj[1].customName || obj[1].name">
                {{ truncateText(obj[1].customName || obj[1].name, 15) }}
              </span>
              <Button
                variant="ghost"
                size="sm"
                @click="startEditing(obj[0], obj[1])"
                class="h-6 w-6 p-0"
              >
                <Pencil class="w-3 h-3" />
              </Button>
            </div>
            <div v-if="obj[1].description && editingId !== obj[0]" class="flex items-start gap-1 mt-1">
              <span class="text-xs text-gray-500 flex-1">
                {{ isExpanded(obj[0]) ? obj[1].description : truncateText(obj[1].description, 10) }}
              </span>
              <button
                v-if="obj[1].description && obj[1].description.length > 10"
                @click="toggleDescription(obj[0])"
                class="text-xs text-gray-700 hover:text-gray-900 flex-shrink-0"
              >
                {{ isExpanded(obj[0]) ? '▲' : '▼' }}
              </button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <CardDescription>
            <!-- Редактирование customName и description -->
            <template v-if="editingId === obj[0]">
              <div class="flex gap-2 mb-4">
                <Input
                  v-model="editingCustomName"
                  placeholder="Название"
                  class="flex-1"
                />
                <Button variant="outline" size="sm" @click="cancelEditing">Отмена</Button>
                <Button size="sm" @click="saveEditing(obj[0])">Сохранить</Button>
              </div>
              <Textarea
                v-model="editingDescription"
                placeholder="Описание"
                class="w-full mb-4 resize-none"
                rows="3"
              />
            </template>
            
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
                @update:model-value="(value) => changeColor(value as string, obj[0])"
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
                @click="emit('openPopup', obj[0]); findOnMap(obj[0])"
                size="default"
                variant="outline"
                :model-value="false"
                >На карте</Toggle
              >
              <Separator class="my-2 w-full" />
              <div v-if="obj[1].type !== 'CircleMarker' && obj[1].type !== 'StopMarker'">
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
                <div class="flex gap-3 flex-wrap" v-if="obj[1].type === 'CircleMarker' || obj[1].type === 'StopMarker'">
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
                    :max="100"
                    :step="1"
                    :min="5"
                    class="mx-auto w-full max-w-xs"
                  />
                </div>
                <div class="flex gap-3 flex-wrap" v-if="obj[1].type !== 'CircleMarker' && obj[1].type !== 'StopMarker'">
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
