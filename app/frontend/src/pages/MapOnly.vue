<script setup lang="ts">
import { Map } from '@/components/Map';
</script>

<template>
  <div class="h-screen w-screen overflow-hidden">
    <Map />
  </div>
</template>

<style scoped>
#map {
  height: 100%;
  width: 100%;
}
</style>
