<script setup lang="ts">
import { SelectLabel, type SelectLabelProps } from "reka-ui";
import { computed, type HTMLAttributes } from "vue";
import { cn } from "@/lib/utils";

const props = defineProps<SelectLabelProps & { class?: HTMLAttributes["class"] }>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;
  return delegated;
});
</script>

<template>
  <SelectLabel
    v-bind="delegatedProps"
    :class="cn('px-2 py-1.5 text-sm font-semibold text-muted-foreground', props.class)"
  >
    <slot />
  </SelectLabel>
</template>
