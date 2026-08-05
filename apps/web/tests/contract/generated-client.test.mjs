import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";


const generatedRoot = resolve(
  process.cwd(),
  "src",
  "generated",
  "api-client",
);
const schema = await readFile(resolve(generatedRoot, "schema.d.ts"), "utf8");
const client = await readFile(resolve(generatedRoot, "client.ts"), "utf8");
const index = await readFile(resolve(generatedRoot, "index.ts"), "utf8");
const combined = schema + client + index;

assert.match(schema, /^\/\/ @generated/m);
assert.match(schema, /Source: contracts\/api\/openapi\.json/);
assert.match(schema, /export interface paths/);
assert.match(
  schema,
  /\/api\/v1\/curriculum\/placements\/\{placement_id\}\/lesson/,
);
assert.match(client, /createClient<paths>/);
assert.match(client, /credentials: "same-origin"/);
assert.doesNotMatch(combined, /financial_ai_academy/);
assert.doesNotMatch(combined, /psycopg|postgres|node:http|node:https/i);
