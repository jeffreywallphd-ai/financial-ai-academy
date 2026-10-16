import { defineConfig, devices } from "@playwright/test";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  browserTestOrigin,
  selectBrowserTestPort,
} from "./support/loopbackPort";


const configDirectory = dirname(fileURLToPath(import.meta.url));
const webRoot = resolve(configDirectory, "..", "..");
const repositoryRoot = resolve(webRoot, "..", "..");
const nodeExecutable = '"' + process.execPath + '"';
const browserTestPort = await selectBrowserTestPort();
const browserTestOriginUrl = browserTestOrigin(browserTestPort);

export default defineConfig({
  testDir: ".",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  outputDir: resolve(repositoryRoot, "artifacts/playwright/wrk0004"),
  use: {
    baseURL: browserTestOriginUrl,
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
      " node_modules/vite/bin/vite.js --host 127.0.0.1 --strictPort --port " +
      browserTestPort,
    cwd: webRoot,
    url: browserTestOriginUrl,
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
