import { readFile, readdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const testDirectory = dirname(fileURLToPath(import.meta.url));
const webRoot = resolve(testDirectory, "..", "..");
const generatedRoot = resolve(webRoot, "src/generated/api-client");
const designSystemRoot = resolve(webRoot, "src/design-system");


async function sourceFiles(directory: string): Promise<string[]> {
  const entries = await readdir(directory, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const path = resolve(directory, entry.name);
    if (entry.isDirectory()) {
      if (
        path.includes(generatedRoot) ||
        path.includes(designSystemRoot)
      ) {
        continue;
      }
      files.push(...(await sourceFiles(path)));
    } else if (entry.name.endsWith(".ts") || entry.name.endsWith(".tsx")) {
      files.push(path);
    }
  }
  return files;
}

describe("static browser boundary", () => {
  it("uses no backend, database, Node server, unsafe HTML, or framework API", async () => {
    const root = resolve(webRoot, "src");
    const files = await sourceFiles(root);
    const source = (
      await Promise.all(files.map((path) => readFile(path, "utf8")))
    ).join("\n");

    expect(source).not.toMatch(
      /financial_ai_academy|psycopg|postgresql|node:http|node:https/,
    );
    expect(source).not.toMatch(
      /dangerouslySetInnerHTML|\.innerHTML|react-router-dom|@react-router\/dev/,
    );
    expect(source).not.toMatch(/next\/|react-server|server action/i);
    expect(source).toMatch(
      /createFinancialAcademyApiClient|FinancialAcademyApiClient/,
    );
  });
});
