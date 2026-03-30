<script setup lang="ts">
import { ref, computed } from "vue";
import { useMapObjectStore } from "@/store";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Download, Upload, Trash2, FileJson } from "lucide-vue-next";

const mapObjectStore = useMapObjectStore();

const open = defineModel<boolean>("open", { default: false });
const emit = defineEmits<{
  imported: [];
}>();

// Фильтр объектов (только Polygon и Polyline)
const geometryObjects = computed(() => {
  const allObjects = Array.from(mapObjectStore.Objects.entries());
  return allObjects.filter(([_, obj]) => 
    obj.type === "Polygon" || obj.type === "Polyline"
  );
});

// Выбранные объекты для экспорта
const selectedIds = ref<Set<string>>(new Set());

// Toggle все/ничего
const allSelected = computed(() => {
  return geometryObjects.value.length > 0 && 
    geometryObjects.value.every(([id]) => selectedIds.value.has(id));
});

const toggleAll = () => {
  if (allSelected.value) {
    selectedIds.value.clear();
  } else {
    geometryObjects.value.forEach(([id]) => {
      selectedIds.value.add(id);
    });
  }
};

// Toggle отдельного объекта
const toggleObject = (id: string) => {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id);
  } else {
    selectedIds.value.add(id);
  }
};

// Экспорт всех объектов
const handleExportAll = async () => {
  try {
    const objects = geometryObjects.value.map(([_, obj]) => obj);
    const data = {
      version: 1,
      exportedAt: new Date().toISOString(),
      count: objects.length,
      objects
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `geometry_export_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    alert(`✅ Экспортировано ${objects.length} объектов`);
    open.value = false;
  } catch (e) {
    console.error("Ошибка экспорта:", e);
    alert(`❌ Ошибка: ${e}`);
  }
};

// Экспорт выбранных объектов
const handleExportSelected = async () => {
  if (selectedIds.value.size === 0) {
    alert("⚠️ Выберите хотя бы один объект для экспорта");
    return;
  }

  try {
    const objects = geometryObjects.value
      .filter(([id]) => selectedIds.value.has(id))
      .map(([_, obj]) => obj);

    const data = {
      version: 1,
      exportedAt: new Date().toISOString(),
      count: objects.length,
      objects
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `geometry_selected_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    alert(`✅ Экспортировано ${objects.length} объектов`);
    open.value = false;
  } catch (e) {
    console.error("Ошибка экспорта:", e);
    alert(`❌ Ошибка: ${e}`);
  }
};

// Импорт из файла
const handleImport = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  try {
    const text = await file.text();
    const data = JSON.parse(text);

    if (!data.objects || !Array.isArray(data.objects)) {
      throw new Error("Неверный формат файла");
    }

    // Импорт через backend
    const useApi = (await import("@/composables/useApi")).default;
    const { createObject } = useApi();
    let importedCount = 0;

    for (const obj of data.objects) {
      try {
        await createObject(obj);
        importedCount++;
      } catch (e) {
        console.error("Ошибка импорта объекта:", obj.id, e);
      }
    }

    alert(`✅ Импортировано ${importedCount} из ${data.objects.length} объектов`);
    emit("imported");
    open.value = false;

    // Очистка input
    target.value = "";
  } catch (e) {
    console.error("Ошибка импорта:", e);
    alert(`❌ Ошибка импорта: ${e}`);
  }
};

// Удаление всех полигонов
const handleDeleteAllPolygons = async () => {
  const polygons = geometryObjects.value.filter(([_, obj]) => obj.type === "Polygon");
  if (polygons.length === 0) {
    alert("ℹ️ Нет полигонов для удаления");
    return;
  }

  if (!confirm(`⚠️ Вы уверены что хотите удалить ${polygons.length} полигонов? Это действие нельзя отменить.`)) {
    return;
  }

  try {
    const useApi = (await import("@/composables/useApi")).default;
    const { deleteObject } = useApi();
    let deletedCount = 0;

    for (const [id] of polygons) {
      try {
        await deleteObject(id);
        mapObjectStore.deleteObject(id);
        deletedCount++;
      } catch (e) {
        console.error("Ошибка удаления:", id, e);
      }
    }

    alert(`✅ Удалено ${deletedCount} полигонов`);
  } catch (e) {
    console.error("Ошибка удаления:", e);
    alert(`❌ Ошибка: ${e}`);
  }
};

// Удаление всех полилиний
const handleDeleteAllPolylines = async () => {
  const polylines = geometryObjects.value.filter(([_, obj]) => obj.type === "Polyline");
  if (polylines.length === 0) {
    alert("ℹ️ Нет полилиний для удаления");
    return;
  }

  if (!confirm(`⚠️ Вы уверены что хотите удалить ${polylines.length} полилиний? Это действие нельзя отменить.`)) {
    return;
  }

  try {
    const useApi = (await import("@/composables/useApi")).default;
    const { deleteObject } = useApi();
    let deletedCount = 0;

    for (const [id] of polylines) {
      try {
        await deleteObject(id);
        mapObjectStore.deleteObject(id);
        deletedCount++;
      } catch (e) {
        console.error("Ошибка удаления:", id, e);
      }
    }

    alert(`✅ Удалено ${deletedCount} полилиний`);
  } catch (e) {
    console.error("Ошибка удаления:", e);
    alert(`❌ Ошибка: ${e}`);
  }
};
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
      <DialogHeader>
        <DialogTitle>Экспорт/Импорт геометрии</DialogTitle>
      </DialogHeader>

      <div class="flex-1 overflow-auto py-4">
        <!-- Статистика -->
        <div class="mb-4 p-4 bg-muted rounded-lg">
          <div class="grid grid-cols-3 gap-4 text-center">
            <div>
              <div class="text-2xl font-bold">{{ geometryObjects.length }}</div>
              <div class="text-sm text-muted-foreground">Всего объектов</div>
            </div>
            <div>
              <div class="text-2xl font-bold">{{ geometryObjects.filter(([_, o]) => o.type === 'Polygon').length }}</div>
              <div class="text-sm text-muted-foreground">Полигоны</div>
            </div>
            <div>
              <div class="text-2xl font-bold">{{ geometryObjects.filter(([_, o]) => o.type === 'Polyline').length }}</div>
              <div class="text-sm text-muted-foreground">Полилинии</div>
            </div>
          </div>
        </div>

        <!-- Кнопки действий -->
        <div class="flex flex-wrap gap-2 mb-4">
          <Button @click="handleExportAll" variant="outline" size="sm">
            <Download class="w-4 h-4 mr-2" />
            Экспорт всех
          </Button>
          <Button 
            @click="handleExportSelected" 
            variant="outline" 
            size="sm"
            :disabled="selectedIds.size === 0"
          >
            <Download class="w-4 h-4 mr-2" />
            Экспорт выбранных ({{ selectedIds.size }})
          </Button>
          <Button variant="outline" size="sm" as-child>
            <label class="cursor-pointer">
              <Upload class="w-4 h-4 mr-2" />
              Импорт
              <input type="file" accept=".json" @change="handleImport" class="hidden" />
            </label>
          </Button>
        </div>

        <!-- Удаление всех -->
        <div class="flex flex-wrap gap-2 mb-4 p-3 bg-destructive/10 rounded-lg">
          <span class="text-sm font-medium text-destructive">Опасная зона:</span>
          <Button 
            @click="handleDeleteAllPolygons" 
            variant="destructive" 
            size="sm"
          >
            <Trash2 class="w-4 h-4 mr-2" />
            Удалить все полигоны
          </Button>
          <Button 
            @click="handleDeleteAllPolylines" 
            variant="destructive" 
            size="sm"
          >
            <Trash2 class="w-4 h-4 mr-2" />
            Удалить все полилинии
          </Button>
        </div>

        <!-- Список объектов -->
        <div class="border rounded-lg">
          <div class="flex items-center justify-between p-3 border-b bg-muted/50">
            <div class="flex items-center gap-2">
              <Checkbox 
                :checked="allSelected" 
                @update:checked="toggleAll"
                id="toggle-all"
              />
              <label for="toggle-all" class="text-sm font-medium cursor-pointer">
                Выбрать все
              </label>
            </div>
            <div class="text-sm text-muted-foreground">
              {{ selectedIds.size }} из {{ geometryObjects.length }} выбрано
            </div>
          </div>

          <div class="divide-y max-h-[400px] overflow-auto">
            <div 
              v-for="[id, obj] in geometryObjects" 
              :key="id"
              class="flex items-center justify-between p-3 hover:bg-muted/50"
            >
              <div class="flex items-center gap-3">
                <Checkbox 
                  :checked="selectedIds.has(id)" 
                  @update:checked="toggleObject(id)"
                  :id="id"
                />
                <div>
                  <div class="font-medium">{{ obj.name || obj.customName || 'Без названия' }}</div>
                  <div class="text-xs text-muted-foreground">
                    {{ obj.type === 'Polygon' ? '🔷 Полигон' : '📏 Полилиния' }} • 
                    {{ obj.coordinates?.[0]?.length || 0 }} точек
                  </div>
                </div>
              </div>
              <div class="text-xs text-muted-foreground font-mono">
                {{ id.slice(0, 8) }}...
              </div>
            </div>

            <div v-if="geometryObjects.length === 0" class="p-8 text-center text-muted-foreground">
              <FileJson class="w-12 h-12 mx-auto mb-2 opacity-50" />
              <div>Нет полигонов или полилиний</div>
            </div>
          </div>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
