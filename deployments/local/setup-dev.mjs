#!/usr/bin/env node

import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const REPOSITORY = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const REQUIRED_NODE = "24.14.0";
const REQUIRED_NPM = "10.8.2";
const FNM_PACKAGE = "Schniz.fnm";
const PINNED_NPM_ROOT = resolve(
  REPOSITORY,
  ".local-codex",
  `npm-${REQUIRED_NPM}`,
);
const PINNED_NPM_CLI = resolve(
  PINNED_NPM_ROOT,
  "node_modules",
  "npm",
  "bin",
  "npm-cli.js",
);
const isWindows = process.platform === "win32";
const rawOptions = process.argv.slice(2);
const options = new Set(rawOptions);
const knownOptions = new Set([
  "--help",
  "--setup-only",
  "--verify-only",
  "--skip-checks",
  "--smoke-start",
]);
const unknownOptions = rawOptions.filter((option) => !knownOptions.has(option));

if (unknownOptions.length) {
  throw new Error(`Unknown option(s): ${unknownOptions.join(", ")}`);
}

if (options.has("--help")) {
  console.log(`
Financial AI Academy development setup

Usage:
  npm --prefix apps/web run setup:dev

Options:
  --setup-only  Install and verify fnm, Node, and npm, then exit.
  --verify-only Install dependencies and run every required check, then exit.
  --skip-checks Start development from existing installed dependencies.
  --smoke-start Stop immediately after both development servers are ready.
  --help        Show this help.

The same npm command works in Git Bash and PowerShell. The setup does not edit
shell profiles or replace the system Node installation.
`.trim());
  process.exit(0);
}

if (options.has("--setup-only") && rawOptions.length !== 1) {
  throw new Error("--setup-only cannot be combined with development options.");
}

function displayArgument(value) {
  return /^[A-Za-z0-9_./:@=$-]+$/.test(value)
    ? value
    : JSON.stringify(value);
}

function displayCommand(command, args) {
  return [command, ...args].map(displayArgument).join(" ");
}

function capture(command, args) {
  const result = spawnSync(command, args, {
    cwd: REPOSITORY,
    encoding: "utf8",
    shell: false,
    windowsHide: true,
  });
  if (result.error || result.status !== 0) {
    return null;
  }
  return result.stdout.trim();
}

async function runChecked(label, command, args) {
  console.log(`\n==> ${label}`);
  console.log(displayCommand(command, args));
  await new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(command, args, {
      cwd: REPOSITORY,
      shell: false,
      stdio: "inherit",
      windowsHide: true,
    });
    child.once("error", rejectPromise);
    child.once("exit", (code, signal) => {
      if (code === 0) {
        resolvePromise();
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

function firstWhereResult(command) {
  if (!isWindows) {
    return null;
  }
  const result = capture("where.exe", [command]);
  return result?.split(/\r?\n/u).find(Boolean) ?? null;
}

function fnmCandidates() {
  const candidates = [];
  if (process.env.FAA_FNM_EXECUTABLE) {
    candidates.push(process.env.FAA_FNM_EXECUTABLE);
  }
  const whereResult = firstWhereResult("fnm");
  if (whereResult) {
    candidates.push(whereResult);
  }
  if (process.env.LOCALAPPDATA) {
    candidates.push(
      join(
        process.env.LOCALAPPDATA,
        "Microsoft",
        "WinGet",
        "Links",
        "fnm.exe",
      ),
    );
    const packages = join(
      process.env.LOCALAPPDATA,
      "Microsoft",
      "WinGet",
      "Packages",
    );
    if (existsSync(packages)) {
      for (const entry of readdirSync(packages, { withFileTypes: true })) {
        if (entry.isDirectory() && entry.name.startsWith(`${FNM_PACKAGE}_`)) {
          candidates.push(join(packages, entry.name, "fnm.exe"));
        }
      }
    }
  }
  if (process.env.USERPROFILE) {
    candidates.push(join(process.env.USERPROFILE, ".fnm", "fnm.exe"));
  }
  return [...new Set(candidates)];
}

function findFnm() {
  if (capture("fnm", ["--version"])) {
    return "fnm";
  }
  for (const candidate of fnmCandidates()) {
    if (existsSync(candidate) && capture(candidate, ["--version"])) {
      return candidate;
    }
  }
  return null;
}

async function installFnm() {
  if (!isWindows) {
    throw new Error(
      "fnm is not available. Install fnm from https://github.com/Schniz/fnm and rerun this command.",
    );
  }
  const winget = firstWhereResult("winget") ?? "winget";
  if (!capture(winget, ["--version"])) {
    throw new Error(
      "fnm and WinGet are unavailable. Install WinGet, then rerun this command.",
    );
  }
  await runChecked(
    "Install fnm with WinGet",
    winget,
    [
      "install",
      "--id",
      FNM_PACKAGE,
      "--exact",
      "--source",
      "winget",
      "--silent",
      "--accept-source-agreements",
      "--accept-package-agreements",
    ],
  );
}

async function prepareRuntime() {
  let fnm = findFnm();
  if (!fnm) {
    await installFnm();
    fnm = findFnm();
  }
  if (!fnm) {
    throw new Error(
      "fnm was installed but is not discoverable yet. Reopen the terminal and rerun the same npm command.",
    );
  }

  const fnmVersion = capture(fnm, ["--version"]);
  console.log(`Using ${fnmVersion ?? "fnm"} from ${fnm}`);
  let nodeVersion = capture(fnm, [
    "exec",
    `--using=${REQUIRED_NODE}`,
    "node",
    "--version",
  ]);
  if (nodeVersion !== `v${REQUIRED_NODE}`) {
    await runChecked(
      `Install Node ${REQUIRED_NODE} with fnm`,
      fnm,
      ["install", REQUIRED_NODE],
    );
    nodeVersion = capture(fnm, [
      "exec",
      `--using=${REQUIRED_NODE}`,
      "node",
      "--version",
    ]);
  }
  if (nodeVersion !== `v${REQUIRED_NODE}`) {
    throw new Error(
      `Expected Node v${REQUIRED_NODE} through fnm, received ${nodeVersion ?? "no version"}.`,
    );
  }

  const nodeExecutable = capture(fnm, [
    "exec",
    `--using=${REQUIRED_NODE}`,
    "node",
    "-p",
    "process.execPath",
  ]);
  if (!nodeExecutable || !existsSync(nodeExecutable)) {
    throw new Error("fnm did not expose the selected Node executable.");
  }
  const bundledNpmCli = resolve(
    dirname(nodeExecutable),
    "node_modules",
    "npm",
    "bin",
    "npm-cli.js",
  );
  if (!existsSync(bundledNpmCli)) {
    throw new Error(
      `Node ${REQUIRED_NODE} does not include the expected npm CLI.`,
    );
  }

  let npmVersion = existsSync(PINNED_NPM_CLI)
    ? capture(fnm, [
        "exec",
        `--using=${REQUIRED_NODE}`,
        "node",
        PINNED_NPM_CLI,
        "--version",
      ])
    : null;
  if (npmVersion !== REQUIRED_NPM) {
    mkdirSync(PINNED_NPM_ROOT, { recursive: true });
    await runChecked(
      `Install project-local npm ${REQUIRED_NPM} for Node ${REQUIRED_NODE}`,
      fnm,
      [
        "exec",
        `--using=${REQUIRED_NODE}`,
        "node",
        bundledNpmCli,
        "install",
        "--global",
        "--prefix",
        PINNED_NPM_ROOT,
        "--no-audit",
        "--no-fund",
        `npm@${REQUIRED_NPM}`,
      ],
    );
    npmVersion = capture(fnm, [
      "exec",
      `--using=${REQUIRED_NODE}`,
      "node",
      PINNED_NPM_CLI,
      "--version",
    ]);
  }
  if (npmVersion !== REQUIRED_NPM) {
    throw new Error(
      `Expected npm ${REQUIRED_NPM} through fnm, received ${npmVersion ?? "no version"}.`,
    );
  }

  console.log(`Runtime ready: Node ${nodeVersion} / npm ${npmVersion}`);
  return { fnm, npmCli: PINNED_NPM_CLI };
}

async function main() {
  process.chdir(REPOSITORY);
  const { fnm, npmCli } = await prepareRuntime();
  if (options.has("--setup-only")) {
    console.log(
      "Setup complete. Run npm --prefix apps/web run setup:dev to verify and start development.",
    );
    return;
  }

  const developmentOptions = rawOptions.filter(
    (option) => option !== "--setup-only",
  );
  const args = [
    "exec",
    `--using=${REQUIRED_NODE}`,
    "node",
    npmCli,
    "--prefix",
    "apps/web",
    "run",
    "dev:full",
  ];
  if (developmentOptions.length) {
    args.push("--", ...developmentOptions);
  }
  await runChecked("Run the complete local development workflow", fnm, args);
}

try {
  await main();
} catch (error) {
  console.error(`\nERROR: ${error instanceof Error ? error.message : error}`);
  process.exitCode = 1;
}
