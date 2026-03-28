<script setup lang="ts">
import { cn } from "@/lib/utils";
import { DialogRoot, type DialogRootEmits, type DialogRootProps, useForwardPropsEmits } from "reka-ui";
import { computed, type HTMLAttributes } from "vue";

const props = defineProps<DialogRootProps & { class?: HTMLAttributes["class"] }>();
const emits = defineEmits<DialogRootEmits>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;
  return delegated;
});

const forwarded = useForwardPropsEmits(delegatedProps, emits);
</script>

<template>
  <DialogRoot v-bind="forwarded">
    <slot />
  </DialogRoot>
</template>
