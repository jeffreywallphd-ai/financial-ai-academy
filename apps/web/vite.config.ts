import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";


export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target:
          process.env.FINANCIAL_AI_ACADEMY_API_ORIGIN ??
          "http://127.0.0.1:8000",
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: true,
    target: "es2024",
  },
  test: {
    environment: "jsdom",
    setupFiles: ["apps/web/tests/unit/setup.ts"],
    include: [
      "apps/web/tests/unit/**/*.test.ts",
      "apps/web/tests/unit/**/*.test.tsx",
      "apps/web/tests/component/**/*.test.ts",
      "apps/web/tests/component/**/*.test.tsx",
    ],
    restoreMocks: true,
  },
});
