import { defineConfig, devices } from "@playwright/test";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";


const configDirectory = dirname(fileURLToPath(import.meta.url));
const webRoot = resolve(configDirectory, "..", "..");
const repositoryRoot = resolve(webRoot, "..", "..");
const nodeExecutable = '"' + process.execPath + '"';

export default defineConfig({
  testDir: ".",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  outputDir: resolve(repositoryRoot, "artifacts/playwright/wrk0004"),
  use: {
    baseURL: "http://127.0.0.1:4174",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  expect: {
    toHaveScreenshot: {
      animations: "disabled",
      maxDiffPixelRatio: 0.01,
    },
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
    command:
      nodeExecutable +
      " node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4174",
    cwd: webRoot,
    url: "http://127.0.0.1:4174",
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
