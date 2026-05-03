import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// Get environment variables for API URLs
const apiUrl = process.env.VITE_API_URL || "http://localhost:5000";
const wsUrl = process.env.VITE_WS_URL || "ws://localhost:5000";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  base: process.env.NODE_ENV === "production" ? "/" : "/",
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: apiUrl,
        changeOrigin: true,
      },
      "/socket.io": {
        target: wsUrl,
        ws: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["vue", "vue-router", "axios"],
        },
      },
    },
  },
  optimizeDeps: {
    include: ["axios", "vue-router"],
  },
  test: {
    globals: true,
    environment: "happy-dom",
    setupFiles: ["./src/test/setup.js"],
    include: ["src/**/*.{test,spec}.{js,mjs}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "json"],
      reportsDirectory: "./coverage",
      include: ["src/**/*.{js,vue}"],
      exclude: ["src/main.js", "src/App.vue"],
    },
  },
});
