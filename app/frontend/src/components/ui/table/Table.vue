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
  <div class="relative w-full overflow-auto">
    <table
      v-bind="delegatedProps"
      :class="cn('w-full caption-bottom text-sm', props.class)"
    >
      <slot />
    </table>
  </div>
</template>
