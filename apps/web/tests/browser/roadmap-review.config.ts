import { defineConfig, devices } from "@playwright/test";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";


const configDirectory = dirname(fileURLToPath(import.meta.url));
const webRoot = resolve(configDirectory, "..", "..");
const repositoryRoot = resolve(webRoot, "..", "..");
const python = process.env.PYTHON ?? "python";

export default defineConfig({
  testDir: "roadmap-review",
  testMatch: "**/*.e2e.ts",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  outputDir: resolve(repositoryRoot, "artifacts/playwright/roadmap-review"),
  use: {
    baseURL: "http://127.0.0.1:8765",
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
  webServer: {
    command: `${python} dev-tools/roadmap-review-site/server.py --port 8765`,
    cwd: repositoryRoot,
    url: "http://127.0.0.1:8765/api/roadmap",
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
