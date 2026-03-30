<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { ComboboxInput, type ComboboxInputProps, useForwardProps } from 'reka-ui'
import { cn } from '@/lib/utils'

const props = defineProps<ComboboxInputProps & { class?: HTMLAttributes['class'] }>()

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props

  return delegated
})

const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <ComboboxInput
    v-bind="forwardedProps"
    :class="cn('flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50', props.class)"
  >
    <slot />
  </ComboboxInput>
</template>
