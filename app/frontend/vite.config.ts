import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  base: "./",
  build: {
    outDir: "dist",
    assetsDir: "assets",
    minify: "esbuild", // Faster than terser
    rollupOptions: {
      input: "index.html",
      output: {
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
              return 'vendor';
            }
            if (id.includes('@deck.gl')) {
              return 'deck';
            }
            if (id.includes('maplibre-gl')) {
              return 'map';
            }
            if (id.includes('shadcn-vue') || id.includes('reka-ui') || id.includes('lucide-vue-next')) {
              return 'ui';
            }
          }
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
