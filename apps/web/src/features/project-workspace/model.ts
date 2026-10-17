import type { components } from "../../generated/api-client";

export type ProjectShell = components["schemas"]["ProjectShellResponseModel"];
export type LearningProjectStartOption =
  components["schemas"]["LearningProjectStartOptionResponseModel"];
export type ProjectWorkspace = components["schemas"]["ProjectWorkspaceResponseModel"];
export type ProjectSnapshot = components["schemas"]["ProjectSnapshotResponseModel"];
export type ProjectArtifact = components["schemas"]["ProjectArtifactResponseModel"];
export type ProjectReference = components["schemas"]["ProjectReferenceResponseModel"];
export type ProjectNote = components["schemas"]["ProjectNoteResponseModel"];
export type ProjectEvidenceExportBundle = components["schemas"]["ProjectEvidenceExportBundleResponseModel"];

export type ProjectListRouteState =
  | { status: "ready"; projects: readonly ProjectShell[]; options: readonly LearningProjectStartOption[] }
  | { status: "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected" };

export type ProjectDetailRouteState =
  | {
      status: "ready";
      project: ProjectShell;
      workspace: ProjectWorkspace;
      snapshots: readonly ProjectSnapshot[];
    }
  | { status: "invalid-selection" | "not-found" | "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected" };

export type ProjectWorkspaceActionState = {
  status: "error";
  kind: "invalid-input" | "stale" | "conflict" | "not-found" | "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected";
  intent: "note" | "reference" | "artifact" | "snapshot";
  idempotencyKey: string;
};

export type ProjectDownloadOutcome =
  | { status: "ready"; bytes: ArrayBuffer; fileName: string; mediaType: string }
  | { status: "not-found" | "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected" };

export type ProjectExportOutcome =
  | { status: "ready"; content: string; fileName: string }
  | { status: "not-found" | "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected" };

export type ProjectCreateRouteState =
  | { status: "ready"; option: LearningProjectStartOption | null; idempotencyKey: string }
  | { status: "invalid-selection" | "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected" };

export type ProjectCreateActionState = {
  status: "error";
  kind: "invalid-input" | "invalid-selection" | "conflict" | "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected";
  idempotencyKey: string;
  draft?: { title: string; charter: string };
};

const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{0,127}$/;
const SEMVER = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/;
const DIGEST = /^[a-f0-9]{64}$/;
const DATE_TIME = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?(Z|[+-](\d{2}):(\d{2}))$/;

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exactKeys(value: Record<string, unknown>, keys: readonly string[]) {
  const actual = Object.keys(value).sort();
  return actual.length === keys.length && keys.slice().sort().every((key, index) => key === actual[index]);
}

function exactOptionalKeys(
  value: Record<string, unknown>,
  required: readonly string[],
  optional: readonly string[] = [],
) {
  const actual = Object.keys(value);
  const accepted = new Set([...required, ...optional]);
  return required.every((key) => Object.hasOwn(value, key))
    && actual.every((key) => accepted.has(key));
}

function text(value: unknown, minimum: number, maximum: number): value is string {
  return typeof value === "string" && value === value.trim() && value.length >= minimum && value.length <= maximum && !/[\0\r\n]/.test(value);
}

function timestamp(value: unknown): value is string {
  if (typeof value !== "string") return false;
  const match = DATE_TIME.exec(value);
  if (!match) return false;
  const [year, month, day, hour, minute, second, offsetHour, offsetMinute] = [
    match[1], match[2], match[3], match[4], match[5], match[6], match[9] ?? "00", match[10] ?? "00",
  ].map(Number);
  if (!year || !month || !day) return false;
  return month <= 12 && day <= new Date(Date.UTC(year, month, 0)).getUTCDate()
    && hour! <= 23 && minute! <= 59 && second! <= 59 && offsetHour! <= 23 && offsetMinute! <= 59
    && !Number.isNaN(Date.parse(value));
}

function utcTimestamp(value: unknown): value is string {
  return typeof value === "string" && value.endsWith("Z") && timestamp(value);
}

function boundedText(value: unknown, minimum: number, maximum: number, allowAngles = false): value is string {
  return typeof value === "string" && value.length >= minimum && value.length <= maximum
    && !value.includes("\0") && (allowAngles || (!value.includes("<") && !value.includes(">")));
}

function positiveInteger(value: unknown): value is number {
  return Number.isInteger(value) && Number(value) >= 1;
}

function digest(value: unknown): value is string {
  return typeof value === "string" && DIGEST.test(value);
}

function optionalBoundedText(value: unknown, maximum: number): boolean {
  return value === undefined || value === null || boundedText(value, 1, maximum);
}

function optionalDigest(value: unknown): boolean {
  return value === undefined || value === null || digest(value);
}

function httpsUrl(value: unknown): value is string {
  if (typeof value !== "string" || value.length > 2048) return false;
  try {
    const parsed = new URL(value);
    const authority = value.slice(value.indexOf("//") + 2).split(/[/?#]/, 1)[0] ?? "";
    return parsed.protocol === "https:" && parsed.hostname !== "" && !authority.includes("@");
  } catch {
    return false;
  }
}

export function logicalPathIsSafe(value: unknown): value is string {
  if (typeof value !== "string" || value.length < 1 || value.length > 240 || value.normalize("NFC") !== value) return false;
  const reserved = /^(?:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\..*)?$/i;
  return !value.includes("\\")
    && !value.startsWith("/")
    && value.split("/").every((segment) => segment !== ""
      && segment !== "."
      && segment !== ".."
      && segment === segment.trim()
      && !segment.endsWith(".")
      && ![...segment].some((character) => character.charCodeAt(0) < 32 || '<>:"|?*'.includes(character))
      && !reserved.test(segment));
}

export function projectIdentifierIsSafe(value: unknown): value is string {
  return typeof value === "string" && IDENTIFIER.test(value);
}

function learningOriginIsSafe(value: unknown): value is components["schemas"]["LearningProjectOriginModel"] {
  if (!record(value) || !exactKeys(value, [
    "origin_type", "project_brief_schema_version", "package_id", "package_version", "package_digest",
    "brief_id", "brief_version", "brief_digest", "curriculum_id", "curriculum_version",
    "curriculum_digest", "placement_id", "placement_version", "placement_digest", "brief_title", "brief_purpose",
  ])) return false;
  return value.origin_type === "learning" && value.project_brief_schema_version === "1.0.0"
    && [value.package_id, value.brief_id, value.curriculum_id, value.placement_id].every(projectIdentifierIsSafe)
    && [value.package_version, value.brief_version, value.curriculum_version, value.placement_version].every(
      (item) => typeof item === "string" && SEMVER.test(item),
    )
    && [value.package_digest, value.brief_digest, value.curriculum_digest, value.placement_digest].every(
      (item) => typeof item === "string" && DIGEST.test(item),
    )
    && text(value.brief_title, 1, 120) && text(value.brief_purpose, 1, 2000);
}

function originIsSafe(value: unknown): boolean {
  return record(value) && value.origin_type === "independent"
    ? exactKeys(value, ["origin_type"])
    : learningOriginIsSafe(value);
}

export function projectShellIsSafe(value: unknown): value is ProjectShell {
  if (!record(value) || !exactKeys(value, [
    "schema_version", "project_id", "learner_id", "title", "charter", "origin",
    "lifecycle", "revision", "created_at", "updated_at",
  ])) return false;
  return value.schema_version === "1.0.0"
    && projectIdentifierIsSafe(value.project_id)
    && projectIdentifierIsSafe(value.learner_id)
    && text(value.title, 1, 120)
    && text(value.charter, 1, 4000)
    && originIsSafe(value.origin)
    && value.lifecycle === "active"
    && Number.isInteger(value.revision) && Number(value.revision) >= 1
    && timestamp(value.created_at) && timestamp(value.updated_at);
}

export function learningProjectStartOptionIsSafe(value: unknown): value is LearningProjectStartOption {
  return record(value)
    && exactKeys(value, ["title", "purpose", "origin"])
    && text(value.title, 1, 120)
    && text(value.purpose, 1, 2000)
    && learningOriginIsSafe(value.origin)
    && value.title === value.origin.brief_title
    && value.purpose === value.origin.brief_purpose;
}

export function projectListIsSafe(value: unknown): value is { records: readonly ProjectShell[] } {
  if (!record(value) || !exactKeys(value, ["records"]) || !Array.isArray(value.records) || value.records.length > 500) return false;
  return value.records.every(projectShellIsSafe)
    && new Set(value.records.map((item) => item.project_id)).size === value.records.length;
}

export function learningStartOptionListIsSafe(value: unknown): value is { records: readonly LearningProjectStartOption[] } {
  if (!record(value) || !exactKeys(value, ["records"]) || !Array.isArray(value.records) || value.records.length > 500) return false;
  return value.records.every(learningProjectStartOptionIsSafe)
    && new Set(value.records.map((item) => item.origin.placement_id)).size === value.records.length;
}

function noteIsSafe(value: unknown): value is ProjectNote {
  return record(value) && exactKeys(value, ["note_id", "note_version", "title", "body", "created_at", "updated_at"])
    && projectIdentifierIsSafe(value.note_id) && positiveInteger(value.note_version)
    && boundedText(value.title, 1, 120) && boundedText(value.body, 1, 20000, true)
    && utcTimestamp(value.created_at) && utcTimestamp(value.updated_at);
}

function referenceIsSafe(value: unknown): value is ProjectReference {
  if (!record(value) || !exactOptionalKeys(value,
    ["reference_id", "reference_version", "title", "url", "source_name", "created_at", "updated_at"],
    ["source_version", "source_digest", "license", "use_constraints"],
  )) return false;
  return projectIdentifierIsSafe(value.reference_id) && positiveInteger(value.reference_version)
    && boundedText(value.title, 1, 160) && httpsUrl(value.url) && boundedText(value.source_name, 1, 160)
    && optionalBoundedText(value.source_version, 128) && optionalDigest(value.source_digest)
    && optionalBoundedText(value.license, 160) && optionalBoundedText(value.use_constraints, 1000)
    && utcTimestamp(value.created_at) && utcTimestamp(value.updated_at);
}

function provenanceIsSafe(value: unknown): boolean {
  if (!record(value) || !exactOptionalKeys(value, ["source_type", "source_title"],
    ["source_version", "source_url", "source_digest", "license", "use_constraints"])) return false;
  const sourceType = String(value.source_type);
  return ["learner_created", "supplied", "external"].includes(sourceType)
    && boundedText(value.source_title, 1, 160)
    && optionalBoundedText(value.source_version, 128)
    && (value.source_url === undefined || value.source_url === null || httpsUrl(value.source_url))
    && optionalDigest(value.source_digest)
    && optionalBoundedText(value.license, 160)
    && optionalBoundedText(value.use_constraints, 1000)
    && (sourceType === "learner_created" || boundedText(value.source_version, 1, 128) || digest(value.source_digest));
}

function environmentIsSafe(value: unknown): boolean {
  if (value === undefined || value === null) return true;
  return record(value) && exactOptionalKeys(value, ["name", "version"], ["dependency_digest"])
    && boundedText(value.name, 1, 120) && boundedText(value.version, 1, 120)
    && optionalDigest(value.dependency_digest);
}

function artifactIsSafe(value: unknown): value is ProjectArtifact {
  if (!record(value) || !exactOptionalKeys(value, [
    "artifact_id", "artifact_version", "artifact_kind", "logical_path", "media_type",
    "inspection_mode", "byte_count", "content_digest", "provenance", "assumptions", "created_at",
  ], ["result_classification", "environment"])) return false;
  const path = value.logical_path;
  const artifactKind = String(value.artifact_kind);
  const mediaType = String(value.media_type);
  const inspectionMode = String(value.inspection_mode);
  const classification = value.result_classification;
  return projectIdentifierIsSafe(value.artifact_id) && positiveInteger(value.artifact_version)
    && ["dataset", "notebook", "code", "environment", "result", "reflection", "supporting_file"].includes(artifactKind)
    && logicalPathIsSafe(path)
    && ["application/octet-stream", "application/json", "application/pdf", "application/x-ipynb+json", "text/csv", "text/markdown", "text/plain", "text/x-python"].includes(mediaType)
    && ["metadata_only", "plain_text"].includes(inspectionMode)
    && (inspectionMode === "metadata_only" || mediaType.startsWith("text/"))
    && Number.isInteger(value.byte_count) && Number(value.byte_count) >= 0 && Number(value.byte_count) <= 10_485_760
    && digest(value.content_digest)
    && (artifactKind === "result"
      ? ["observed", "calculated", "simulated", "predicted", "generated", "narrative"].includes(String(classification))
      : classification === undefined || classification === null || classification === "narrative")
    && provenanceIsSafe(value.provenance) && environmentIsSafe(value.environment)
    && Array.isArray(value.assumptions) && value.assumptions.length <= 20
    && value.assumptions.every((item) => boundedText(item, 1, 4000))
    && utcTimestamp(value.created_at);
}

function domainLinkIsSafe(value: unknown): boolean {
  if (!record(value) || !exactOptionalKeys(value, [
    "link_id", "link_type", "owner_module", "resource_type", "resource_id", "owner_reference_digest",
    "target_status", "provenance", "validated_at", "created_at",
  ], ["resource_version", "resource_as_of"])) return false;
  return projectIdentifierIsSafe(value.link_id)
    && ["context", "input", "comparison", "output"].includes(String(value.link_type))
    && projectIdentifierIsSafe(value.owner_module) && projectIdentifierIsSafe(value.resource_type)
    && projectIdentifierIsSafe(value.resource_id) && digest(value.owner_reference_digest)
    && value.target_status === "available" && boundedText(value.provenance, 1, 1000)
    && optionalBoundedText(value.resource_version, 128)
    && (value.resource_as_of === undefined || value.resource_as_of === null || utcTimestamp(value.resource_as_of))
    && (typeof value.resource_version === "string" || typeof value.resource_as_of === "string")
    && utcTimestamp(value.validated_at) && utcTimestamp(value.created_at);
}

export function projectWorkspaceIsSafe(value: unknown, project?: ProjectShell): value is ProjectWorkspace {
  if (!record(value) || !exactKeys(value, [
    "schema_version", "project_id", "learner_id", "workspace_revision", "notes", "references",
    "artifacts", "domain_links", "created_at", "updated_at",
  ])) return false;
  if (value.schema_version !== "1.0.0" || !projectIdentifierIsSafe(value.project_id)
    || !projectIdentifierIsSafe(value.learner_id) || !positiveInteger(value.workspace_revision)
    || !utcTimestamp(value.created_at) || !utcTimestamp(value.updated_at)) return false;
  if (project && (value.project_id !== project.project_id || value.learner_id !== project.learner_id)) return false;
  if (!Array.isArray(value.notes) || value.notes.length > 50 || !value.notes.every(noteIsSafe)
    || !Array.isArray(value.references) || value.references.length > 50 || !value.references.every(referenceIsSafe)
    || !Array.isArray(value.artifacts) || value.artifacts.length > 100 || !value.artifacts.every(artifactIsSafe)
    || !Array.isArray(value.domain_links) || value.domain_links.length > 50 || !value.domain_links.every(domainLinkIsSafe)) return false;
  return new Set(value.notes.map((item) => item.note_id)).size === value.notes.length
    && new Set(value.references.map((item) => item.reference_id)).size === value.references.length
    && new Set(value.artifacts.map((item) => `${item.artifact_id}@${item.artifact_version}`)).size === value.artifacts.length
    && new Set(value.domain_links.map((item) => item.link_id)).size === value.domain_links.length;
}

function versionReferenceIsSafe(value: unknown): boolean {
  return record(value) && exactKeys(value, ["record_id", "record_version", "record_digest"])
    && projectIdentifierIsSafe(value.record_id) && positiveInteger(value.record_version) && digest(value.record_digest);
}

function artifactReferenceIsSafe(value: unknown): boolean {
  return record(value) && exactKeys(value, ["artifact_id", "artifact_version", "manifest_digest", "content_digest", "byte_count"])
    && projectIdentifierIsSafe(value.artifact_id) && positiveInteger(value.artifact_version)
    && digest(value.manifest_digest) && digest(value.content_digest)
    && Number.isInteger(value.byte_count) && Number(value.byte_count) >= 0 && Number(value.byte_count) <= 10_485_760;
}

function linkReferenceIsSafe(value: unknown): boolean {
  return record(value) && exactKeys(value, ["link_id", "record_digest", "owner_reference_digest"])
    && projectIdentifierIsSafe(value.link_id) && digest(value.record_digest) && digest(value.owner_reference_digest);
}

export function projectSnapshotIsSafe(value: unknown, project?: ProjectShell): value is ProjectSnapshot {
  if (!record(value) || !exactKeys(value, ["schema_version", "snapshot_id", "snapshot_digest", "snapshot", "closed_at"])
    || value.schema_version !== "1.0.0" || !projectIdentifierIsSafe(value.snapshot_id)
    || !digest(value.snapshot_digest) || !utcTimestamp(value.closed_at) || !record(value.snapshot)) return false;
  const material = value.snapshot;
  if (!exactKeys(material, [
    "project_id", "learner_id", "project_revision", "project_shell_digest", "workspace_revision",
    "workspace_created_at", "workspace_updated_at", "notes", "references", "artifacts", "domain_links",
  ]) || !projectIdentifierIsSafe(material.project_id) || !projectIdentifierIsSafe(material.learner_id)
    || !positiveInteger(material.project_revision) || !digest(material.project_shell_digest)
    || !positiveInteger(material.workspace_revision) || !utcTimestamp(material.workspace_created_at)
    || !utcTimestamp(material.workspace_updated_at)) return false;
  if (project && (material.project_id !== project.project_id || material.learner_id !== project.learner_id)) return false;
  if (!(Array.isArray(material.notes) && material.notes.length <= 50 && material.notes.every(versionReferenceIsSafe)
    && Array.isArray(material.references) && material.references.length <= 50 && material.references.every(versionReferenceIsSafe)
    && Array.isArray(material.artifacts) && material.artifacts.length <= 100 && material.artifacts.every(artifactReferenceIsSafe)
    && Array.isArray(material.domain_links) && material.domain_links.length <= 50 && material.domain_links.every(linkReferenceIsSafe))) return false;
  return new Set(material.notes.map((item) => item.record_id)).size === material.notes.length
    && new Set(material.references.map((item) => item.record_id)).size === material.references.length
    && new Set(material.artifacts.map((item) => item.artifact_id)).size === material.artifacts.length
    && new Set(material.domain_links.map((item) => item.link_id)).size === material.domain_links.length;
}

export function projectSnapshotListIsSafe(value: unknown, project?: ProjectShell): value is { records: readonly ProjectSnapshot[] } {
  return record(value) && exactKeys(value, ["records"]) && Array.isArray(value.records)
    && value.records.length <= 500 && value.records.every((item) => projectSnapshotIsSafe(item, project))
    && new Set(value.records.map((item) => item.snapshot_id)).size === value.records.length;
}

function evidenceArtifactFileIsSafe(value: unknown): boolean {
  return record(value) && exactKeys(value, ["artifact_id", "artifact_version", "byte_count", "content_digest", "logical_path", "manifest_digest", "media_type"])
    && projectIdentifierIsSafe(value.artifact_id) && positiveInteger(value.artifact_version)
    && Number.isInteger(value.byte_count) && Number(value.byte_count) >= 0 && Number(value.byte_count) <= 10_485_760
    && digest(value.content_digest) && digest(value.manifest_digest)
    && logicalPathIsSafe(value.logical_path)
    && typeof value.media_type === "string" && value.media_type.length >= 1 && value.media_type.length <= 160;
}

function excludedArtifactIsSafe(value: unknown): boolean {
  return record(value) && exactKeys(value, ["artifact_id", "artifact_version", "reason"])
    && projectIdentifierIsSafe(value.artifact_id) && positiveInteger(value.artifact_version)
    && ["source_use_restricted", "not_authorized", "content_unavailable"].includes(String(value.reason));
}

function evidenceFileContentIsSafe(value: unknown): boolean {
  return record(value) && exactKeys(value, ["artifact_id", "artifact_version", "content_base64", "logical_path"])
    && projectIdentifierIsSafe(value.artifact_id) && positiveInteger(value.artifact_version)
    && typeof value.content_base64 === "string" && value.content_base64.length <= 14_000_000
    && /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(value.content_base64)
    && logicalPathIsSafe(value.logical_path);
}

export function projectEvidenceExportBundleIsSafe(
  value: unknown,
  projectId: string,
  snapshotId: string,
): value is ProjectEvidenceExportBundle {
  if (!record(value) || !exactKeys(value, ["manifest", "files"]) || !record(value.manifest) || !Array.isArray(value.files)
    || !exactKeys(value.manifest, ["schema_version", "export_id", "export_digest", "generated_at", "export"])
    || value.manifest.schema_version !== "1.0.0" || !projectIdentifierIsSafe(value.manifest.export_id)
    || !digest(value.manifest.export_digest) || !utcTimestamp(value.manifest.generated_at) || !record(value.manifest.export)) return false;
  const material = value.manifest.export;
  if (!exactKeys(material, ["artifact_files", "excluded_artifacts", "format", "project_id", "snapshot_digest", "snapshot_id", "snapshot_record", "workspace_record"])
    || material.format !== "project-evidence-manifest-v1" || material.project_id !== projectId || material.snapshot_id !== snapshotId
    || !digest(material.snapshot_digest) || !projectSnapshotIsSafe(material.snapshot_record)
    || !projectWorkspaceIsSafe(material.workspace_record)
    || material.snapshot_record.snapshot_id !== snapshotId || material.snapshot_record.snapshot_digest !== material.snapshot_digest
    || material.snapshot_record.snapshot.project_id !== projectId || material.workspace_record.project_id !== projectId
    || material.snapshot_record.snapshot.learner_id !== material.workspace_record.learner_id
    || material.snapshot_record.snapshot.workspace_revision !== material.workspace_record.workspace_revision
    || material.snapshot_record.snapshot.workspace_created_at !== material.workspace_record.created_at
    || material.snapshot_record.snapshot.workspace_updated_at !== material.workspace_record.updated_at
    || !Array.isArray(material.artifact_files) || material.artifact_files.length > 100 || !material.artifact_files.every(evidenceArtifactFileIsSafe)
    || !Array.isArray(material.excluded_artifacts) || material.excluded_artifacts.length > 100 || !material.excluded_artifacts.every(excludedArtifactIsSafe)
    || value.files.length > 100 || !value.files.every(evidenceFileContentIsSafe)) return false;
  const included = new Map(material.artifact_files.map((file) => [`${file.artifact_id}@${file.artifact_version}`, file]));
  const excluded = new Set(material.excluded_artifacts.map((file) => `${file.artifact_id}@${file.artifact_version}`));
  const snapshotted = new Map(material.snapshot_record.snapshot.artifacts.map((file) => [`${file.artifact_id}@${file.artifact_version}`, file]));
  if (included.size !== material.artifact_files.length || excluded.size !== material.excluded_artifacts.length
    || [...included.keys()].some((key) => excluded.has(key))
    || included.size + excluded.size !== snapshotted.size
    || [...snapshotted.keys()].some((key) => !included.has(key) && !excluded.has(key))
    || [...included].some(([key, file]) => {
      const reference = snapshotted.get(key);
      return !reference || reference.byte_count !== file.byte_count || reference.content_digest !== file.content_digest
        || reference.manifest_digest !== file.manifest_digest;
    })) return false;
  const contentKeys = value.files.map((file) => `${file.artifact_id}@${file.artifact_version}`);
  return new Set(contentKeys).size === contentKeys.length && contentKeys.length === included.size
    && value.files.every((file) => included.get(`${file.artifact_id}@${file.artifact_version}`)?.logical_path === file.logical_path);
}

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (record(value)) {
    return `{${Object.keys(value).filter((key) => value[key] !== null && value[key] !== undefined).sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

async function canonicalDigest(value: unknown): Promise<string> {
  const bytes = new TextEncoder().encode(canonicalJson(value));
  const measured = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(measured)].map((item) => item.toString(16).padStart(2, "0")).join("");
}

async function versionReferencesMatch(
  references: readonly { readonly record_id: string; readonly record_version: number; readonly record_digest: string }[],
  records: readonly Record<string, unknown>[],
  idKey: string,
  versionKey: string,
): Promise<boolean> {
  if (references.length !== records.length) return false;
  for (let index = 0; index < records.length; index += 1) {
    const reference = references[index]!;
    const item = records[index]!;
    if (reference.record_id !== item[idKey] || reference.record_version !== item[versionKey]
      || reference.record_digest !== await canonicalDigest(item)) return false;
  }
  return true;
}

export async function projectEvidenceExportBindingsAreSafe(value: ProjectEvidenceExportBundle): Promise<boolean> {
  const material = value.manifest.export;
  const snapshot = material.snapshot_record;
  const workspace = material.workspace_record;
  if (snapshot.snapshot_digest !== await canonicalDigest(snapshot.snapshot)
    || value.manifest.export_digest !== await canonicalDigest(material)
    || !await versionReferencesMatch(snapshot.snapshot.notes, workspace.notes as unknown as readonly Record<string, unknown>[], "note_id", "note_version")
    || !await versionReferencesMatch(snapshot.snapshot.references, workspace.references as unknown as readonly Record<string, unknown>[], "reference_id", "reference_version")) return false;

  if (snapshot.snapshot.artifacts.length !== workspace.artifacts.length
    || snapshot.snapshot.domain_links.length !== workspace.domain_links.length) return false;
  for (let index = 0; index < workspace.artifacts.length; index += 1) {
    const reference = snapshot.snapshot.artifacts[index]!;
    const artifact = workspace.artifacts[index]!;
    if (reference.artifact_id !== artifact.artifact_id || reference.artifact_version !== artifact.artifact_version
      || reference.manifest_digest !== await canonicalDigest(artifact)) return false;
  }
  for (let index = 0; index < workspace.domain_links.length; index += 1) {
    const reference = snapshot.snapshot.domain_links[index]!;
    const link = workspace.domain_links[index]!;
    if (reference.link_id !== link.link_id || reference.owner_reference_digest !== link.owner_reference_digest
      || reference.record_digest !== await canonicalDigest(link)) return false;
  }

  const artifacts = new Map(workspace.artifacts.map((artifact) => [`${artifact.artifact_id}@${artifact.artifact_version}`, artifact]));
  for (const file of material.artifact_files) {
    const artifact = artifacts.get(`${file.artifact_id}@${file.artifact_version}`);
    if (!artifact || file.manifest_digest !== await canonicalDigest(artifact)
      || file.logical_path !== artifact.logical_path || file.media_type !== artifact.media_type
      || file.byte_count !== artifact.byte_count || file.content_digest !== artifact.content_digest) return false;
  }
  return true;
}

export function readableProjectDate(value: string): string {
  return new Intl.DateTimeFormat("en", { day: "numeric", month: "short", timeZone: "UTC", year: "numeric" }).format(new Date(value));
}
