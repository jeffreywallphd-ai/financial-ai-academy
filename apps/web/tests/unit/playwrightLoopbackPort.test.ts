import { createServer, type Server } from "node:net";
import { afterEach, describe, expect, it } from "vitest";

import {
  browserTestOrigin,
  selectBrowserTestPort,
} from "../browser/support/loopbackPort";


const servers: Server[] = [];
const originalBrowserTestPort =
  process.env.FINANCIAL_AI_ACADEMY_BROWSER_TEST_PORT;

async function occupyEphemeralLoopbackPort(): Promise<number> {
  const server = createServer();
  servers.push(server);
  await new Promise<void>((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  if (address === null || typeof address === "string") {
    throw new Error("Expected an occupied loopback port.");
  }
  return address.port;
}

afterEach(async () => {
  await Promise.all(
    servers.splice(0).map(
      (server) =>
        new Promise<void>((resolve, reject) => {
          server.close((error) => (error ? reject(error) : resolve()));
        }),
    ),
  );
  if (originalBrowserTestPort === undefined) {
    delete process.env.FINANCIAL_AI_ACADEMY_BROWSER_TEST_PORT;
  } else {
    process.env.FINANCIAL_AI_ACADEMY_BROWSER_TEST_PORT =
      originalBrowserTestPort;
  }
});

describe("Playwright loopback port isolation", () => {
  it("allocates an available port instead of colliding with an occupied one", async () => {
    delete process.env.FINANCIAL_AI_ACADEMY_BROWSER_TEST_PORT;
    const occupiedPort = await occupyEphemeralLoopbackPort();

    const selectedPort = await selectBrowserTestPort();

    expect(selectedPort).not.toBe(occupiedPort);
    expect(process.env.FINANCIAL_AI_ACADEMY_BROWSER_TEST_PORT).toBe(
      String(selectedPort),
    );
    expect(browserTestOrigin(selectedPort)).toBe(
      `http://127.0.0.1:${selectedPort}`,
    );
  });

  it("supports a validated explicit port for bounded diagnostics", async () => {
    await expect(selectBrowserTestPort("43117")).resolves.toBe(43117);
    await expect(selectBrowserTestPort("not-a-port")).rejects.toThrow(
      "must be an integer",
    );
    await expect(selectBrowserTestPort("65536")).rejects.toThrow(
      "must be between",
    );
  });
});
