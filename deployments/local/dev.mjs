#!/usr/bin/env node

import { spawn, spawnSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  rmSync,
} from "node:fs";
import { createServer } from "node:net";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const REPOSITORY = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const WEB_DIRECTORY = resolve(REPOSITORY, "apps/web");
const BACKEND_DIRECTORY = resolve(REPOSITORY, "backend");
const LOCAL_STATE = resolve(REPOSITORY, ".local-codex");
const TOOL_VENV = resolve(LOCAL_STATE, "dev-runner-venv");
const TOOL_PYTHON = resolve(
  TOOL_VENV,
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
);
const BACKEND_PYTHON = resolve(
  BACKEND_DIRECTORY,
  process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python",
);
const COMPOSE_FILE = resolve(
  REPOSITORY,
  "deployments/local/compose.qualify.yml",
);
const REQUIRED_NODE_MAJOR = 24;
const REQUIRED_NPM = "10.8.2";
const REQUIRED_UV = "0.11.29";
const API_PORT = 8000;
const WEB_PORT = 5173;
const API_ORIGIN = `http://127.0.0.1:${API_PORT}`;
const WEB_ORIGIN = `http://127.0.0.1:${WEB_PORT}`;
const COMPOSE_PROJECT = `faa-dev-${process.pid}-${Date.now()}`;
const DATA_ROOT = resolve(
  REPOSITORY,
  `.test-data/approved-lesson-dev-${process.pid}-${Date.now()}`,
);

const npmCli = process.env.npm_execpath;
if (!npmCli || !existsSync(npmCli)) {
  throw new Error(
    "Run this file through npm: npm --prefix apps/web run dev:full",
  );
}
const npmCommand = process.execPath;
const npmPrefix = [npmCli];

const options = new Set(process.argv.slice(2));
const knownOptions = new Set([
  "--help",
  "--verify-only",
  "--skip-checks",
  "--smoke-start",
]);
const unknownOptions = [...options].filter((option) => !knownOptions.has(option));
if (unknownOptions.length) {
  throw new Error(`Unknown option(s): ${unknownOptions.join(", ")}`);
}

if (options.has("--help")) {
  console.log(`
Financial AI Academy local development runner

Usage:
  npm --prefix apps/web run dev:full

Options:
  --verify-only  Install dependencies and run every required check, then exit.
  --skip-checks  Start development from existing installed dependencies.
  --smoke-start  Stop immediately after both development servers are ready.
  --help         Show this help.
`.trim());
  process.exit(0);
}

if (options.has("--verify-only") && options.has("--smoke-start")) {
  throw new Error("--verify-only and --smoke-start cannot be combined.");
}

const verifyOnly = options.has("--verify-only");
const skipChecks = options.has("--skip-checks");
const smokeStart = options.has("--smoke-start");
const isWindows = process.platform === "win32";
const ownedProcesses = new Set();
let activeProcess = null;
let interrupted = false;
let composeStarted = false;
let postgresPort = null;

function displayArgument(value) {
  return /^[A-Za-z0-9_./:@=-]+$/.test(value)
    ? value
    : JSON.stringify(value);
}

function displayCommand(command, args) {
  return [command, ...args].map(displayArgument).join(" ");
}

function capture(command, args, environment = process.env) {
  const result = spawnSync(command, args, {
    cwd: REPOSITORY,
    encoding: "utf8",
    env: environment,
    shell: false,
    windowsHide: true,
  });
  if (result.error || result.status !== 0) {
    return null;
  }
  return result.stdout.trim();
}

async function runChecked(label, command, args, environment = process.env) {
  console.log(`\n==> ${label}`);
  console.log(displayCommand(command, args));
  await new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(command, args, {
      cwd: REPOSITORY,
      detached: !isWindows,
      env: environment,
      shell: false,
      stdio: "inherit",
      windowsHide: true,
    });
    activeProcess = child;
    child.once("error", (error) => {
      if (activeProcess === child) {
        activeProcess = null;
      }
      rejectPromise(error);
    });
    child.once("exit", (code, signal) => {
      if (activeProcess === child) {
        activeProcess = null;
      }
      if (code === 0) {
        resolvePromise();
      } else if (interrupted) {
        rejectPromise(new Error("Development runner interrupted."));
      } else {
        rejectPromise(
          new Error(
            `${label} failed with ${
              signal ? `signal ${signal}` : `exit code ${code}`
            }.`,
          ),
        );
      }
    });
  });
}

function stopProcess(child) {
  if (!child || child.exitCode !== null || child.signalCode !== null) {
    return;
  }
  if (isWindows) {
    spawnSync(
      "taskkill",
      ["/pid", String(child.pid), "/t", "/f"],
      { stdio: "ignore", windowsHide: true },
    );
  } else {
    try {
      process.kill(-child.pid, "SIGTERM");
    } catch (error) {
      if (error.code !== "ESRCH") {
        throw error;
      }
    }
  }
}

function stopOwnedProcesses() {
  stopProcess(activeProcess);
  for (const child of ownedProcesses) {
    stopProcess(child);
  }
}

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => {
    if (!interrupted) {
      interrupted = true;
      console.log("\nStopping the local development environment...");
      stopOwnedProcesses();
    }
  });
}

function findPython314() {
  const candidates = isWindows
    ? [
        ["py", ["-3.14"]],
        ["python", []],
      ]
    : [
        ["python3.14", []],
        ["python3", []],
        ["python", []],
      ];
  for (const [command, prefix] of candidates) {
    const version = capture(command, [
      ...prefix,
      "-c",
      "import sys; print('.'.join(map(str, sys.version_info[:3])))",
    ]);
    if (version?.startsWith("3.14.")) {
      return { command, prefix, version };
    }
  }
  throw new Error(
    "CPython 3.14 is required. Install it and ensure py -3.14 (Windows) or python3.14 is available.",
  );
}

function checkPrerequisites() {
  const nodeMajor = Number(process.versions.node.split(".", 1)[0]);
  if (nodeMajor !== REQUIRED_NODE_MAJOR) {
    throw new Error(
      `Node ${REQUIRED_NODE_MAJOR} is required; this command is running Node ${process.versions.node}. Run npm --prefix apps/web run setup:dev to use the project runtime.`,
    );
  }
  const npmVersion = capture(npmCommand, [...npmPrefix, "--version"]);
  if (npmVersion !== REQUIRED_NPM) {
    throw new Error(
      `npm ${REQUIRED_NPM} is required; this command is running npm ${npmVersion ?? "unavailable"}.`,
    );
  }
  const dockerVersion = capture("docker", [
    "version",
    "--format",
    "{{.Server.Version}}",
  ]);
  if (!dockerVersion) {
    throw new Error(
      "Docker Desktop/Engine must be installed and running for the disposable PostgreSQL database.",
    );
  }
  const composeVersion = capture("docker", ["compose", "version"]);
  if (!composeVersion) {
    throw new Error("Docker Compose is required.");
  }
  const gitVersion = capture("git", ["--version"]);
  if (!gitVersion) {
    throw new Error("Git is required for the repository integrity check.");
  }
  const python = findPython314();
  console.log("Prerequisites");
  console.log(`- Node ${process.versions.node} / npm ${npmVersion}`);
  console.log(`- Python ${python.version}`);
  console.log(`- Docker ${dockerVersion} / ${composeVersion}`);
  console.log(`- ${gitVersion}`);
  return python;
}

function recreateManagedToolVenvIfNeeded(python) {
  if (existsSync(TOOL_PYTHON)) {
    const version = capture(TOOL_PYTHON, [
      "-c",
      "import sys; print('.'.join(map(str, sys.version_info[:2])))",
    ]);
    if (version === "3.14") {
      return;
    }
    const relativePath = relative(LOCAL_STATE, TOOL_VENV);
    if (
      relativePath.startsWith("..") ||
      relativePath === "" ||
      resolve(LOCAL_STATE, relativePath) !== TOOL_VENV
    ) {
      throw new Error("Refusing to replace an unexpected tool environment.");
    }
    rmSync(TOOL_VENV, { force: true, recursive: true });
  }
  mkdirSync(LOCAL_STATE, { recursive: true });
  const result = spawnSync(
    python.command,
    [...python.prefix, "-m", "venv", TOOL_VENV],
    {
      cwd: REPOSITORY,
      shell: false,
      stdio: "inherit",
      windowsHide: true,
    },
  );
  if (result.error || result.status !== 0) {
    throw new Error("Unable to create the ignored local runner environment.");
  }
}

async function installDependencies(python) {
  recreateManagedToolVenvIfNeeded(python);
  const uvVersion = capture(TOOL_PYTHON, ["-m", "uv", "--version"]);
  if (
    uvVersion !== `uv ${REQUIRED_UV}` &&
    !uvVersion?.startsWith(`uv ${REQUIRED_UV} (`)
  ) {
    await runChecked(
      `Install uv ${REQUIRED_UV} in the ignored local tool environment`,
      TOOL_PYTHON,
      [
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--upgrade",
        `uv==${REQUIRED_UV}`,
      ],
    );
  }
  await runChecked(
    "Restore the exact Python environment",
    TOOL_PYTHON,
    ["-m", "uv", "sync", "--project", "backend", "--frozen"],
  );
  await runChecked(
    "Restore the exact web environment",
    npmCommand,
    [...npmPrefix, "--prefix", "apps/web", "ci"],
  );
  await runChecked(
    "Install pinned Chromium",
    npmCommand,
    [
      ...npmPrefix,
      "--prefix",
      "apps/web",
      "exec",
      "--",
      "playwright",
      "install",
      "chromium",
    ],
  );
}

function requirePreparedDependencies() {
  if (!existsSync(BACKEND_PYTHON)) {
    throw new Error(
      "The backend environment is absent; rerun without --skip-checks.",
    );
  }
  if (!existsSync(resolve(WEB_DIRECTORY, "node_modules"))) {
    throw new Error(
      "The web environment is absent; rerun without --skip-checks.",
    );
  }
}

function getFreeLoopbackPort() {
  return new Promise((resolvePromise, rejectPromise) => {
    const server = createServer();
    server.unref();
    server.once("error", rejectPromise);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : null;
      server.close((error) => {
        if (error) {
          rejectPromise(error);
        } else if (!port) {
          rejectPromise(new Error("Unable to allocate a loopback port."));
        } else {
          resolvePromise(port);
        }
      });
    });
  });
}

function assertLoopbackPortAvailable(port, label) {
  return new Promise((resolvePromise, rejectPromise) => {
    const server = createServer();
    server.unref();
    server.once("error", () => {
      rejectPromise(
        new Error(`${label} port ${port} is already in use.`),
      );
    });
    server.listen(port, "127.0.0.1", () => {
      server.close((error) => {
        if (error) {
          rejectPromise(error);
        } else {
          resolvePromise();
        }
      });
    });
  });
}

function composeEnvironment() {
  return {
    ...process.env,
    FAA_QUALIFICATION_POSTGRES_PORT: String(postgresPort),
  };
}

function composeArguments(action) {
  return [
    "compose",
    "-p",
    COMPOSE_PROJECT,
    "-f",
    COMPOSE_FILE,
    ...action,
  ];
}

async function startPostgres() {
  const maximumAttempts = 5;
  for (let attempt = 1; attempt <= maximumAttempts; attempt += 1) {
    postgresPort = await getFreeLoopbackPort();
    composeStarted = true;
    try {
      await runChecked(
        "Start disposable PostgreSQL 18.4",
        "docker",
        composeArguments(["up", "-d", "--wait"]),
        composeEnvironment(),
      );
      return;
    } catch (error) {
      stopPostgres();
      if (attempt === maximumAttempts) {
        throw new Error(
          `Unable to start disposable PostgreSQL after ${maximumAttempts} loopback-port attempts. Last failure: ${
            error instanceof Error ? error.message : error
          }`,
        );
      }
      console.warn(
        `PostgreSQL port ${postgresPort} was rejected; retrying with a new loopback port (${attempt}/${maximumAttempts}).`,
      );
    }
  }
}

function stopPostgres() {
  if (!composeStarted) {
    return;
  }
  const result = spawnSync(
    "docker",
    composeArguments(["down", "--volumes"]),
    {
      cwd: REPOSITORY,
      env: composeEnvironment(),
      shell: false,
      stdio: "inherit",
      windowsHide: true,
    },
  );
  composeStarted = false;
  if (result.error || result.status !== 0) {
    console.error(
      "WARNING: Docker Compose cleanup failed. Use the printed project name for exact manual cleanup:",
      COMPOSE_PROJECT,
    );
  }
}

function qualificationEnvironment() {
  return {
    ...process.env,
    FINANCIAL_AI_ACADEMY_E2E_EXTERNAL_DB_ACKNOWLEDGED: "true",
    FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE: process.execPath,
    FINANCIAL_AI_ACADEMY_NPM_CLI: npmCli,
    FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN: postgresDsn(),
    PYTHONPATH: resolve(BACKEND_DIRECTORY, "src"),
  };
}

function postgresDsn() {
  return `postgresql://financial_ai_academy:qualification-only@127.0.0.1:${postgresPort}/financial_ai_academy`;
}

async function runAllChecks() {
  const environment = qualificationEnvironment();
  await runChecked(
    "Run backend contract, unit, integration, API, and architecture tests",
    BACKEND_PYTHON,
    ["-m", "pytest", "backend/tests"],
    environment,
  );
  await runChecked(
    "Verify the reviewed OpenAPI snapshot",
    BACKEND_PYTHON,
    [
      "-m",
      "financial_ai_academy.hosts.api.generate_openapi",
      "--check",
    ],
    environment,
  );
  await runChecked(
    "Verify the generated browser client",
    npmCommand,
    [...npmPrefix, "--prefix", "apps/web", "run", "generate:api", "--", "--check"],
  );
  await runChecked(
    "Type-check the web application",
    npmCommand,
    [...npmPrefix, "--prefix", "apps/web", "run", "typecheck"],
  );
  await runChecked(
    "Lint the web application",
    npmCommand,
    [...npmPrefix, "--prefix", "apps/web", "run", "lint"],
  );
  await runChecked(
    "Run web unit and component tests",
    npmCommand,
    [...npmPrefix, "--prefix", "apps/web", "test", "--", "--run"],
  );
  await runChecked(
    "Build the static browser application",
    npmCommand,
    [...npmPrefix, "--prefix", "apps/web", "run", "build"],
  );
  await runChecked(
    "Run focused Chromium qualification",
    npmCommand,
    [
      ...npmPrefix,
      "--prefix",
      "apps/web",
      "run",
      "test:browser",
      "--",
      "apps/web/tests/browser/lesson-reading",
    ],
  );
  await runChecked(
    "Run live cross-system qualification",
    BACKEND_PYTHON,
    [
      "tests/e2e/approved-lesson/run.py",
      "--postgres-dsn",
      postgresDsn(),
    ],
    environment,
  );
  for (const [label, script] of [
    ["Run architecture fitness functions", "dev-tools/architecture/check_architecture.py"],
    ["Run security fitness functions", "dev-tools/security/check_slice_security.py"],
    ["Check the design system", "dev-tools/design/check_design_system.py"],
    ["Check documentation", "dev-tools/documentation/check_docs.py"],
    ["Check planning integrity", "dev-tools/planning/check_planning.py"],
    ["Check aggregate agent readiness", "dev-tools/agent/check_ready.py"],
  ]) {
    await runChecked(label, BACKEND_PYTHON, [script], environment);
  }
  await runChecked(
    "Review JavaScript dependency advisories",
    npmCommand,
    [...npmPrefix, "--prefix", "apps/web", "audit", "--audit-level=high"],
  );
  await runChecked("Check Git whitespace integrity", "git", ["diff", "--check"]);
}

function startOwned(label, command, args, environment = process.env) {
  console.log(`\n==> Start ${label}`);
  console.log(displayCommand(command, args));
  const child = spawn(command, args, {
    cwd: REPOSITORY,
    detached: !isWindows,
    env: environment,
    shell: false,
    stdio: "inherit",
    windowsHide: true,
  });
  ownedProcesses.add(child);
  child.once("exit", () => ownedProcesses.delete(child));
  return child;
}

async function waitForHttp(url, child, label) {
  const deadline = Date.now() + 45_000;
  while (Date.now() < deadline) {
    if (child.exitCode !== null || child.signalCode !== null) {
      throw new Error(`${label} exited before it became ready.`);
    }
    try {
      const response = await fetch(url, {
        signal: AbortSignal.timeout(1_000),
      });
      if (response.ok) {
        return;
      }
    } catch {
      // Readiness polling is expected to fail until the server has bound.
    }
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 250));
  }
  throw new Error(`${label} did not become ready within 45 seconds.`);
}

function waitForDevelopmentExit(api, web) {
  return new Promise((resolvePromise, rejectPromise) => {
    const handleExit = (label) => (code, signal) => {
      if (interrupted) {
        resolvePromise();
      } else {
        rejectPromise(
          new Error(
            `${label} stopped unexpectedly (${
              signal ? `signal ${signal}` : `exit code ${code}`
            }).`,
          ),
        );
      }
    };
    api.once("exit", handleExit("Python API"));
    web.once("exit", handleExit("Vite"));
  });
}

function removeOwnedDataRoot() {
  if (!existsSync(DATA_ROOT)) {
    return;
  }
  const parent = resolve(REPOSITORY, ".test-data");
  const relativePath = relative(parent, DATA_ROOT);
  if (
    relativePath.startsWith("..") ||
    relativePath.includes("/") ||
    relativePath.includes(String.fromCharCode(92)) ||
    !relativePath.startsWith("approved-lesson-dev-")
  ) {
    throw new Error("Refusing to remove an unexpected development data root.");
  }
  rmSync(DATA_ROOT, { force: true, recursive: true });
}

async function startDevelopment() {
  await assertLoopbackPortAvailable(API_PORT, "Python API");
  await assertLoopbackPortAvailable(WEB_PORT, "Vite");
  mkdirSync(DATA_ROOT, { recursive: true });
  const environment = qualificationEnvironment();
  const api = startOwned(
    "Python API",
    BACKEND_PYTHON,
    [
      "deployments/local/serve.py",
      "--postgres-dsn",
      postgresDsn(),
      "--data-root",
      DATA_ROOT,
      "--host",
      "127.0.0.1",
      "--port",
      String(API_PORT),
      "--seed-approved-fixture",
      "--api-only",
      "--public-origin",
      WEB_ORIGIN,
      "--allowed-host",
      `127.0.0.1:${WEB_PORT}`,
      "--allowed-host",
      `127.0.0.1:${API_PORT}`,
    ],
    environment,
  );
  const web = startOwned(
    "Vite development server",
    npmCommand,
    [...npmPrefix, "--prefix", "apps/web", "run", "dev"],
    {
      ...process.env,
      FINANCIAL_AI_ACADEMY_API_ORIGIN: API_ORIGIN,
    },
  );
  await Promise.all([
    waitForHttp(`${API_ORIGIN}/ready`, api, "Python API"),
    waitForHttp(WEB_ORIGIN, web, "Vite"),
  ]);
  console.log("\nDevelopment environment is ready:");
  console.log(
    `- Application: ${WEB_ORIGIN}/learn/placements/intro-risk-return-primary`,
  );
  console.log(`- API readiness: ${API_ORIGIN}/ready`);
  console.log("- Press Ctrl+C to stop the servers and disposable database.");
  if (!smokeStart) {
    await waitForDevelopmentExit(api, web);
  }
}

async function main() {
  process.chdir(REPOSITORY);
  const python = checkPrerequisites();
  if (skipChecks) {
    requirePreparedDependencies();
  } else {
    await installDependencies(python);
  }
  await startPostgres();
  if (!skipChecks) {
    await runAllChecks();
  }
  if (verifyOnly) {
    console.log("\nAll required installs and checks passed.");
    return;
  }
  if (!skipChecks) {
    stopPostgres();
    await startPostgres();
  }
  await startDevelopment();
}

try {
  await main();
} catch (error) {
  if (interrupted) {
    process.exitCode = 130;
  } else {
    console.error(`\nERROR: ${error instanceof Error ? error.message : error}`);
    process.exitCode = 1;
  }
} finally {
  stopOwnedProcesses();
  stopPostgres();
  try {
    removeOwnedDataRoot();
  } catch (error) {
    console.error(
      `WARNING: ${error instanceof Error ? error.message : error}`,
    );
    process.exitCode ||= 1;
  }
}
