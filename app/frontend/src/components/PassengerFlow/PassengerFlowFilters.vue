<script setup lang="ts">
import { computed } from "vue";
import { useMapObjectStore } from "@/store";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Route } from "lucide-vue-next";

const mapObjectStore = useMapObjectStore();

const flows = computed(() => mapObjectStore.passengerFlows);

const toggleFlow = (flowId: string) => {
  mapObjectStore.togglePassengerFlowVisibility(flowId);
};
</script>

<template>
  <div class="space-y-3 p-3 border rounded-lg bg-card">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <Route class="w-4 h-4 text-primary" />
        <h3 class="font-semibold text-sm">Пассажиропотоки</h3>
      </div>
      <span class="text-xs text-muted-foreground">{{ flows.length }}</span>
    </div>

    <div v-if="flows.length === 0" class="text-sm text-muted-foreground italic">
      Нет созданных потоков
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="flow in flows"
        :key="flow.flow_id"
        class="flex items-center gap-2"
      >
        <Checkbox
          :id="flow.flow_id"
          :checked="mapObjectStore.isPassengerFlowVisible(flow.flow_id)"
          @update:checked="toggleFlow(flow.flow_id)"
        />
        <Label
          :for="flow.flow_id"
          class="text-sm font-normal cursor-pointer flex-1"
        >
          <div class="flex items-center justify-between">
            <span>{{ flow.name }}</span>
            <span class="text-xs text-muted-foreground">
              {{ flow.stops_count }} ост. • {{ flow.total_passengers }} пасс.
            </span>
          </div>
        </Label>
      </div>
    </div>
  </div>
</template>
