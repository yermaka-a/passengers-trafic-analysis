<script setup lang="ts">
import { DialogPortal, type DialogPortalProps, useForwardProps } from "reka-ui";
import { computed, type HTMLAttributes } from "vue";

const props = defineProps<DialogPortalProps & { class?: HTMLAttributes["class"] }>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;
  return delegated;
});

const forwardedProps = useForwardProps(delegatedProps);
</script>

<template>
  <DialogPortal v-bind="forwardedProps">
    <slot />
  </DialogPortal>
</template>
