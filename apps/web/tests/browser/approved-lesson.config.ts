import { defineConfig, devices } from "@playwright/test";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";


const configDirectory = dirname(fileURLToPath(import.meta.url));
const webRoot = resolve(configDirectory, "..", "..");
const repositoryRoot = resolve(webRoot, "..", "..");

export default defineConfig({
  testDir: "approved-lesson",
  testMatch: "**/*.e2e.ts",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  outputDir: resolve(repositoryRoot, "artifacts/playwright/wrk0005"),
  use: {
    baseURL:
      process.env.FINANCIAL_AI_ACADEMY_E2E_BASE_URL ??
      "http://127.0.0.1:8000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        colorScheme: "light",
      },
    },
  ],
});
