<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { ComboboxContent, type ComboboxContentProps, useForwardProps } from 'reka-ui'
import { cn } from '@/lib/utils'

const props = defineProps<ComboboxContentProps & { class?: HTMLAttributes['class'] }>()

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props

  return delegated
})

const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <ComboboxContent
    v-bind="forwardedProps"
    :class="cn('max-h-[300px] overflow-y-auto overflow-x-hidden', props.class)"
  >
    <div role="presentation">
      <slot />
    </div>
  </ComboboxContent>
</template>
