<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, Trash2, Edit, ArrowLeftRight } from "lucide-vue-next";
import PassengerFlowEditor from "@/components/PassengerFlow/PassengerFlowEditor.vue";

interface PassengerFlow {
  flow_id: string;
  name: string;
  date: string;
  direction: string;
  stops_count: number;
}

const flows = ref<PassengerFlow[]>([]);
const showEditor = ref(false);
const editingFlow = ref<any>(null);
const loading = ref(false);

// Загрузить все потоки
const loadFlows = async () => {
  loading.value = true;
  try {
    const { get_all_passenger_flows } = (window as any).pywebview?.api || {};
    if (!get_all_passenger_flows) {
      console.error("API недоступно");
      return;
    }
    
    const result = await get_all_passenger_flows({});
    if (result?.status === "success" && result.flows) {
      flows.value = result.flows;
    }
  } catch (e) {
    console.error("loadFlows error:", e);
  } finally {
    loading.value = false;
  }
};

// Создать новый поток
const createNewFlow = () => {
  editingFlow.value = null;
  showEditor.value = true;
};

// Редактировать поток
const editFlow = async (flow: PassengerFlow) => {
  try {
    const { get_passenger_flow } = (window as any).pywebview?.api || {};
    if (!get_passenger_flow) return;
    
    const result = await get_passenger_flow({ flow_id: flow.flow_id });
    if (result?.status === "success" && result.flow) {
      editingFlow.value = result.flow;
      showEditor.value = true;
    }
  } catch (e) {
    console.error("editFlow error:", e);
  }
};

// Удалить поток
const deleteFlow = async (flowId: string) => {
  if (!confirm("Вы уверены что хотите удалить этот пассажиропоток?")) return;
  
  try {
    const { delete_passenger_flow } = (window as any).pywebview?.api || {};
    if (!delete_passenger_flow) return;
    
    const result = await delete_passenger_flow({ flow_id: flowId });
    if (result?.status === "success") {
      await loadFlows();
    } else {
      alert(`❌ Ошибка: ${result?.message}`);
    }
  } catch (e) {
    console.error("deleteFlow error:", e);
    alert(`❌ Ошибка: ${e}`);
  }
};

// Переключить направление
const toggleDirection = async (flowId: string) => {
  try {
    const flow = flows.value.find(f => f.flow_id === flowId);
    if (!flow) return;
    
    const { update_passenger_flow } = (window as any).pywebview?.api || {};
    if (!update_passenger_flow) return;
    
    const newDirection = flow.direction === "forward" ? "backward" : "forward";
    const result = await update_passenger_flow({
      flow_id: flowId,
      direction: newDirection
    });
    
    if (result?.status === "success") {
      flow.direction = newDirection;
    }
  } catch (e) {
    console.error("toggleDirection error:", e);
  }
};

// Обработчик сохранения
const handleSaved = () => {
  loadFlows();
};

onMounted(() => {
  loadFlows();
});
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between px-8 py-4 border-b">
      <h1 class="text-2xl font-semibold">Пассажиропотоки</h1>
      <Button @click="createNewFlow">
        <Plus class="w-4 h-4 mr-2" />
        Добавить поток
      </Button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-auto p-8">
      <Card>
        <CardHeader>
          <CardTitle>Список пассажиропотоков</CardTitle>
        </CardHeader>
        <CardContent>
          <div v-if="loading" class="text-center py-8 text-muted-foreground">
            Загрузка...
          </div>
          
          <Table v-else-if="flows.length > 0">
            <TableHeader>
              <TableRow>
                <TableHead>Название</TableHead>
                <TableHead>Дата</TableHead>
                <TableHead>Направление</TableHead>
                <TableHead>Остановки</TableHead>
                <TableHead class="text-right">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="flow in flows" :key="flow.flow_id">
                <TableCell class="font-medium">{{ flow.name }}</TableCell>
                <TableCell>{{ flow.date }}</TableCell>
                <TableCell>
                  <Badge :variant="flow.direction === 'forward' ? 'default' : 'secondary'">
                    {{ flow.direction === 'forward' ? 'Прямое →' : 'Обратное ←' }}
                  </Badge>
                </TableCell>
                <TableCell>{{ flow.stops_count }}</TableCell>
                <TableCell class="text-right">
                  <div class="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="toggleDirection(flow.flow_id)"
                      title="Переключить направление"
                    >
                      <ArrowLeftRight class="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="editFlow(flow)"
                      title="Редактировать"
                    >
                      <Edit class="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="deleteFlow(flow.flow_id)"
                      title="Удалить"
                      class="text-destructive hover:text-destructive"
                    >
                      <Trash2 class="w-4 h-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
          
          <div v-else class="text-center py-8 text-muted-foreground">
            Нет пассажиропотоков. Создайте первый!
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Editor -->
    <PassengerFlowEditor
      v-model:open="showEditor"
      @saved="handleSaved"
    />
  </div>
</template>
