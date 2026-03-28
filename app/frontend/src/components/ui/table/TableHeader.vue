<script setup lang="ts">
import { cn } from "@/lib/utils";
import { computed, type HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;

  return delegated;
});
</script>

<template>
  <thead v-bind="delegatedProps" :class="cn('[&_tr]:border-b', props.class)">
    <slot />
  </thead>
</template>
