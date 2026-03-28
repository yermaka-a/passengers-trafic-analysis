<script setup lang="ts">
import { RouterView } from 'vue-router';
</script>

<template>
  <RouterView />
</template>

<style>
/* Глобальные стили для fullscreen */
html, body, #app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style>
