<script setup lang="ts">
import { cn } from "@/lib/utils";
import { SelectRoot, type SelectRootEmits, type SelectRootProps, useForwardPropsEmits } from "reka-ui";
import { computed, type HTMLAttributes } from "vue";

const props = defineProps<SelectRootProps & { class?: HTMLAttributes["class"] }>();
const emits = defineEmits<SelectRootEmits>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;
  return delegated;
});

const forwarded = useForwardPropsEmits(delegatedProps, emits);
</script>

<template>
  <SelectRoot v-bind="forwarded">
    <slot />
  </SelectRoot>
</template>
