<script setup lang="ts">
import { SelectValue, type SelectValueProps } from "reka-ui";
import { computed, type HTMLAttributes } from "vue";
import { cn } from "@/lib/utils";

const props = defineProps<SelectValueProps & { class?: HTMLAttributes["class"] }>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;
  return delegated;
});
</script>

<template>
  <SelectValue v-bind="delegatedProps" :class="cn('text-foreground', props.class)">
    <slot />
  </SelectValue>
</template>
