<script setup lang="ts">
import { ref } from 'vue';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Label } from '@/components/ui/label';
import { LayoutDashboard } from 'lucide-vue-next';
import { useLayoutStore, type MapPosition } from '@/store/useLayoutStore';

const layoutStore = useLayoutStore();
const open = ref(false);

const setMapPosition = (position: MapPosition) => {
  layoutStore.setMapPosition(position);
  open.value = false;
};
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button variant="outline" size="sm" class="cursor-pointer" title="Настройки раскладки">
        <LayoutDashboard class="h-4 w-4" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto">
      <div class="space-y-2">
        <div class="space-y-2">
          <Label class="text-xs font-semibold">Позиция карты</Label>
          <div class="grid grid-cols-2 gap-1.5">
            <Button
              variant="outline"
              size="sm"
              :class="{ 'bg-accent text-accent-foreground': layoutStore.layout.mapPosition === 'top' }"
              @click="setMapPosition('top')"
              class="cursor-pointer text-xs px-2 py-1 h-auto"
            >
              ⬆ Сверху
            </Button>
            <Button
              variant="outline"
              size="sm"
              :class="{ 'bg-accent text-accent-foreground': layoutStore.layout.mapPosition === 'bottom' }"
              @click="setMapPosition('bottom')"
              class="cursor-pointer text-xs px-2 py-1 h-auto"
            >
              Снизу ⬇
            </Button>
            <Button
              variant="outline"
              size="sm"
              :class="{ 'bg-accent text-accent-foreground': layoutStore.layout.mapPosition === 'left' }"
              @click="setMapPosition('left')"
              class="cursor-pointer text-xs px-2 py-1 h-auto"
            >
              ⬅ Слева
            </Button>
            <Button
              variant="outline"
              size="sm"
              :class="{ 'bg-accent text-accent-foreground': layoutStore.layout.mapPosition === 'right' }"
              @click="setMapPosition('right')"
              class="cursor-pointer text-xs px-2 py-1 h-auto"
            >
              Справа ➡
            </Button>
          </div>
        </div>
      </div>
    </PopoverContent>
  </Popover>
</template>
