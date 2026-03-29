<script setup lang="ts">
import { SelectGroup, type SelectGroupProps } from "reka-ui";
import { computed, type HTMLAttributes } from "vue";
import { cn } from "@/lib/utils";

const props = defineProps<SelectGroupProps & { class?: HTMLAttributes["class"] }>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;
  return delegated;
});
</script>

<template>
  <SelectGroup
    v-bind="delegatedProps"
    :class="cn('p-1 w-full', props.class)"
  >
    <slot />
  </SelectGroup>
</template>
