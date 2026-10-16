import { createServer } from "node:net";


const LOOPBACK_HOST = "127.0.0.1";
const MIN_PORT = 1;
const MAX_PORT = 65_535;

function parsePort(value: string): number {
  if (!/^\d+$/.test(value)) {
    throw new Error("Browser test port must be an integer.");
  }
  const port = Number(value);
  if (!Number.isSafeInteger(port) || port < MIN_PORT || port > MAX_PORT) {
    throw new Error(
      `Browser test port must be between ${MIN_PORT} and ${MAX_PORT}.`,
    );
  }
  return port;
}

async function allocateAvailableLoopbackPort(): Promise<number> {
  return await new Promise<number>((resolve, reject) => {
    const server = createServer();
    server.unref();
    server.once("error", reject);
    server.listen(0, LOOPBACK_HOST, () => {
      const address = server.address();
      if (address === null || typeof address === "string") {
        server.close();
        reject(new Error("Could not allocate a loopback browser test port."));
        return;
      }
      const port = address.port;
      server.close((error) => {
        if (error) {
          reject(error);
          return;
        }
        resolve(port);
      });
    });
  });
}

export async function selectBrowserTestPort(
  explicitPort = process.env.FINANCIAL_AI_ACADEMY_BROWSER_TEST_PORT,
): Promise<number> {
  const port =
    explicitPort === undefined
      ? await allocateAvailableLoopbackPort()
      : parsePort(explicitPort);
  // Playwright reloads its config in worker processes. Persist the one
  // per-run choice so every worker inherits the same isolated origin.
  process.env.FINANCIAL_AI_ACADEMY_BROWSER_TEST_PORT = String(port);
  return port;
}

export function browserTestOrigin(port: number): string {
  return `http://${LOOPBACK_HOST}:${port}`;
}
