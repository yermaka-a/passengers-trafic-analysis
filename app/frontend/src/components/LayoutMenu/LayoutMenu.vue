<script setup lang="ts">
import { ref } from 'vue';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { LayoutDashboard, RotateCcw } from 'lucide-vue-next';
import { useLayoutStore, type MapPosition } from '@/store/useLayoutStore';

const layoutStore = useLayoutStore();
const open = ref(false);

const setMapPosition = (position: MapPosition) => {
  layoutStore.setMapPosition(position);
  open.value = false;
};

const resetLayout = () => {
  if (confirm('Сбросить layout к значениям по умолчанию?')) {
    layoutStore.resetLayout();
  }
};
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button variant="outline" size="sm" class="cursor-pointer" title="Настройки раскладки">
        <LayoutDashboard class="h-4 w-4" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-64">
      <div class="space-y-4">
        <div class="space-y-2">
          <Label>Позиция карты</Label>
          <div class="grid grid-cols-2 gap-2">
            <Button
              variant="outline"
              size="sm"
              :class="{ 'bg-accent text-accent-foreground': layoutStore.layout.mapPosition === 'top' }"
              @click="setMapPosition('top')"
              class="cursor-pointer"
            >
              ⬆ Сверху
            </Button>
            <Button
              variant="outline"
              size="sm"
              :class="{ 'bg-accent text-accent-foreground': layoutStore.layout.mapPosition === 'bottom' }"
              @click="setMapPosition('bottom')"
              class="cursor-pointer"
            >
              Снизу ⬇
            </Button>
            <Button
              variant="outline"
              size="sm"
              :class="{ 'bg-accent text-accent-foreground': layoutStore.layout.mapPosition === 'left' }"
              @click="setMapPosition('left')"
              class="cursor-pointer"
            >
              ⬅ Слева
            </Button>
            <Button
              variant="outline"
              size="sm"
              :class="{ 'bg-accent text-accent-foreground': layoutStore.layout.mapPosition === 'right' }"
              @click="setMapPosition('right')"
              class="cursor-pointer"
            >
              Справа ➡
            </Button>
          </div>
        </div>
        
        <Separator />
        
        <Button
          variant="outline"
          size="sm"
          class="w-full cursor-pointer"
          @click="resetLayout"
        >
          <RotateCcw class="h-4 w-4 mr-2" />
          Сбросить layout
        </Button>
      </div>
    </PopoverContent>
  </Popover>
</template>
