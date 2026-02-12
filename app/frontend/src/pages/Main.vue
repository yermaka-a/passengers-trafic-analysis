<script setup lang="ts">
import { MainHeader } from "@/components/MainHeader";
import { Map } from "@/components/Map";
import { List } from "@/components/List";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import BrushTable from "@/components/BrushTable/BrushTable.vue";
</script>

<template>
  <MainHeader class="p-4 bg-secondary grad rounded-b-3xl" />
  <ResizablePanelGroup
    direction="horizontal"
    class="max-w-dvwx min-h-11/12 rounded-lg border"
  >
    <ResizablePanel :default-size="50">
      <ResizablePanelGroup direction="vertical">
        <ResizablePanel :default-size="25">
          <BrushTable />
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel :default-size="75">
          <List />
        </ResizablePanel>
      </ResizablePanelGroup>
    </ResizablePanel>

    <ResizableHandle withHandle />

    <ResizablePanel :default-size="100">
      <Map />
    </ResizablePanel>
  </ResizablePanelGroup>
</template>

<style scoped></style>
