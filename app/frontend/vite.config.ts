import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: "./",
  build: {
    outDir: "dist",
    assetsDir: "assets",
    minify: "esbuild", // Faster than terser
    rollupOptions: {
      input: "index.html",
      output: {
        manualChunks: {
          // Split vendor chunks for better caching
          vendor: ["vue", "pinia", "vue-router"],
          deck: ["@deck.gl/core", "@deck.gl/layers", "@deck.gl/mapbox", "@deck.gl/extensions"],
          map: ["maplibre-gl"],
          ui: ["shadcn-vue", "reka-ui", "lucide-vue-next"],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  css: {
    devSourcemap: false, // Disable in dev for faster builds
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
    extensions: [".vue", ".ts", ".json"],
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ["vue", "pinia", "@deck.gl/core", "@deck.gl/layers", "maplibre-gl"],
  },
});
