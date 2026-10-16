#!/usr/bin/env python3
"""Check changed learner-facing copy without turning style advice into a gate."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


REPORT_SCHEMA = "learner-language-report-v1"
RULES_SCHEMA = "learner-language-rules-v1"
DEFAULT_CONFIG = "dev-tools/learner-language/rules.json"
EXCEPTION_MARKER = "learner-language:"
EXCEPTION_RE = re.compile(
    r"learner-language:\s*allow\s+([a-z0-9.-]+)\s*;\s*"
    r"reason=([^;]+?)\s*;\s*explained=([^*\n]+?)\s*(?:\*/)?\s*(?:})?\s*$",
    re.IGNORECASE,
)
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
ATTRIBUTE_TEMPLATE = r"(?:{attributes})\s*=\s*(?:\"([^\"]+)\"|'([^']+)'|\{{\s*\"([^\"]+)\"\s*\}}|\{{\s*'([^']+)'\s*\}})"
STRING_RE = re.compile(r"(?<![A-Za-z0-9_])(?:\"([^\"\\]*(?:\\.[^\"\\]*)*)\"|'([^'\\]*(?:\\.[^'\\]*)*)')")
JSX_TEXT_RE = re.compile(r">\s*([^<>{}\n][^<>{}\n]*?)\s*<")
ACRONYM_RE = re.compile(r"\b[A-Z]{3,6}\b")
WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")


class CheckError(RuntimeError):
    """A bounded invocation, configuration, source, or Git error."""


@dataclass(frozen=True)
class Rule:
    identifier: str
    pattern: re.Pattern[str]
    replacement: str
    message: str


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    path: str
    line: int
    message: str
    replacement: str | None = None


@dataclass(frozen=True)
class ExceptionDirective:
    rule_id: str
    line: int
    target_line: int
    reason: str
    explanation: str


@dataclass(frozen=True)
class Configuration:
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    technical_record_labels: tuple[str, ...]
    visible_attributes: tuple[str, ...]
    blocking_rules: tuple[Rule, ...]
    sentence_word_limit: int
    possible_jargon: tuple[str, ...]
    acronym_allowlist: frozenset[str]


def repository_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "docs").is_dir():
            return candidate
    raise CheckError("Unable to locate a repository root containing .git and docs.")


def _require_string_list(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item.strip() for item in value):
        raise CheckError(f"{label} must be a non-empty array of strings.")
    return tuple(item.strip() for item in value)


def load_configuration(path: Path) -> Configuration:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exception:
        raise CheckError(f"Unable to read learner-language configuration: {exception}") from exception
    if not isinstance(payload, dict) or payload.get("schema_version") != RULES_SCHEMA:
        raise CheckError(f"Configuration schema_version must be {RULES_SCHEMA}.")

    raw_rules = payload.get("blocking_rules")
    if not isinstance(raw_rules, list) or not raw_rules:
        raise CheckError("blocking_rules must be a non-empty array.")
    rules: list[Rule] = []
    identifiers: set[str] = set()
    for index, raw in enumerate(raw_rules):
        if not isinstance(raw, dict):
            raise CheckError(f"blocking_rules[{index}] must be an object.")
        identifier = raw.get("id")
        pattern = raw.get("pattern")
        replacement = raw.get("replacement")
        message = raw.get("message")
        if not all(isinstance(item, str) and item.strip() for item in (identifier, pattern, replacement, message)):
            raise CheckError(f"blocking_rules[{index}] requires id, pattern, replacement, and message strings.")
        if not re.fullmatch(r"[a-z0-9.-]+", identifier) or identifier in identifiers:
            raise CheckError(f"Invalid or duplicate blocking rule id: {identifier}")
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
        except re.error as exception:
            raise CheckError(f"Invalid pattern for {identifier}: {exception}") from exception
        if compiled.match(""):
            raise CheckError(f"Blocking rule {identifier} must not match an empty string.")
        identifiers.add(identifier)
        rules.append(Rule(identifier, compiled, replacement.strip(), message.strip()))

    advisory = payload.get("advisory")
    if not isinstance(advisory, dict):
        raise CheckError("advisory must be an object.")
    sentence_limit = advisory.get("sentence_word_limit")
    if not isinstance(sentence_limit, int) or not 20 <= sentence_limit <= 80:
        raise CheckError("advisory.sentence_word_limit must be an integer from 20 through 80.")

    return Configuration(
        include=_require_string_list(payload.get("include"), "include"),
        exclude=tuple(payload.get("exclude", ())),
        technical_record_labels=_require_string_list(
            payload.get("technical_record_labels"), "technical_record_labels"
        ),
        visible_attributes=_require_string_list(payload.get("visible_attributes"), "visible_attributes"),
        blocking_rules=tuple(rules),
        sentence_word_limit=sentence_limit,
        possible_jargon=tuple(str(item).casefold() for item in advisory.get("possible_jargon", ())),
        acronym_allowlist=frozenset(str(item) for item in advisory.get("acronym_allowlist", ())),
    )


def _matches(path: str, patterns: Sequence[str]) -> bool:
    normalized = path.replace("\\", "/")
    candidate = PurePosixPath(normalized)
    return any(candidate.match(pattern) or fnmatch.fnmatchcase(normalized, pattern) for pattern in patterns)


def owned_path(path: str, configuration: Configuration) -> bool:
    return _matches(path, configuration.include) and not _matches(path, configuration.exclude)


def _git(root: Path, arguments: Sequence[str], *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode and not allow_failure:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown Git error"
        raise CheckError(f"Git source selection failed: {detail}")
    return completed


def _parse_changed_lines(diff: str) -> dict[str, set[int]]:
    selected: dict[str, set[int]] = {}
    path: str | None = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            value = line[4:].strip()
            if value == "/dev/null":
                path = None
            else:
                path = value[2:] if value.startswith("b/") else value
                selected.setdefault(path.replace("\\", "/"), set())
            continue
        match = HUNK_RE.match(line)
        if match and path is not None:
            start = int(match.group(1))
            count = int(match.group(2) or "1")
            selected[path].update(range(start, start + count))
    return selected


def _merge_lines(target: dict[str, set[int]], source: dict[str, set[int]]) -> None:
    for path, lines in source.items():
        target.setdefault(path, set()).update(lines)


def changed_lines(root: Path, base_ref: str | None) -> dict[str, set[int]]:
    arguments = ["diff", "--ignore-all-space", "--unified=0", "--no-ext-diff", "--no-color"]
    if base_ref:
        verified = _git(root, ["rev-parse", "--verify", f"{base_ref}^{{commit}}"], allow_failure=True)
        if verified.returncode:
            raise CheckError(f"Base revision does not resolve to a commit: {base_ref}")
        diff = _git(root, [*arguments, base_ref, "--"]).stdout
        selected = _parse_changed_lines(diff)
    else:
        head = _git(root, ["rev-parse", "--verify", "HEAD^{commit}"], allow_failure=True)
        if head.returncode == 0:
            selected = _parse_changed_lines(_git(root, [*arguments, "HEAD", "--"]).stdout)
        else:
            selected = {}
            _merge_lines(selected, _parse_changed_lines(_git(root, [*arguments, "--cached", "--"]).stdout))
            _merge_lines(selected, _parse_changed_lines(_git(root, [*arguments, "--"]).stdout))

    untracked = _git(root, ["ls-files", "--others", "--exclude-standard", "-z"]).stdout
    for raw in untracked.split("\0"):
        if not raw:
            continue
        path = raw.replace("\\", "/")
        source = root / path
        if source.is_file():
            selected[path] = set(range(1, len(source.read_text(encoding="utf-8").splitlines()) + 1))
    return selected


def all_owned_lines(root: Path, configuration: Configuration) -> dict[str, set[int]]:
    tracked = _git(root, ["ls-files", "-z"]).stdout
    selected: dict[str, set[int]] = {}
    for raw in tracked.split("\0"):
        path = raw.replace("\\", "/")
        if raw and owned_path(path, configuration):
            source = root / path
            if source.is_file():
                selected[path] = set(range(1, len(source.read_text(encoding="utf-8").splitlines()) + 1))
    return selected


def _technical_record_lines(lines: Sequence[str], labels: Sequence[str]) -> set[int]:
    spans: list[tuple[int, int]] = []
    stack: list[int] = []
    for index, line in enumerate(lines, start=1):
        opening = len(re.findall(r"<details\b", line, re.IGNORECASE))
        closing = len(re.findall(r"</details\s*>", line, re.IGNORECASE))
        stack.extend([index] * opening)
        for _ in range(closing):
            if not stack:
                continue
            start = stack.pop()
            block = "\n".join(lines[start - 1 : index])
            if any(re.search(rf"<summary\b[^>]*>\s*{re.escape(label)}\s*</summary\s*>", block, re.IGNORECASE) for label in labels):
                spans.append((start, index))
    ignored: set[int] = set()
    for start, end in spans:
        ignored.update(range(start, end + 1))
    return ignored


def _strip_comments(lines: Sequence[str]) -> list[str]:
    cleaned: list[str] = []
    in_block = False
    for original in lines:
        line = original
        output = ""
        index = 0
        while index < len(line):
            if in_block:
                end = line.find("*/", index)
                if end < 0:
                    index = len(line)
                    continue
                in_block = False
                index = end + 2
                continue
            start = line.find("/*", index)
            slash = line.find("//", index)
            if slash >= 0 and (start < 0 or slash < start):
                output += line[index:slash]
                index = len(line)
                continue
            if start < 0:
                output += line[index:]
                index = len(line)
                continue
            output += line[index:start]
            in_block = True
            index = start + 2
        cleaned.append(output)
    return cleaned


def _candidate_fragments(line: str, configuration: Configuration) -> tuple[str, ...]:
    fragments: list[str] = []
    attributes = "|".join(re.escape(item) for item in configuration.visible_attributes)
    attribute_re = re.compile(ATTRIBUTE_TEMPLATE.format(attributes=attributes), re.IGNORECASE)
    for match in attribute_re.finditer(line):
        fragments.append(next(value for value in match.groups() if value is not None))
    fragments.extend(match.group(1).strip() for match in JSX_TEXT_RE.finditer(line))
    if not re.match(r"^\s*(?:import|export\s+.+\s+from)\b", line):
        for match in STRING_RE.finditer(line):
            fragments.append(next(value for value in match.groups() if value is not None))
    return tuple(dict.fromkeys(value for value in fragments if value.strip()))


def _directives(
    raw_lines: Sequence[str], selected: set[int], known_rules: set[str]
) -> tuple[dict[tuple[int, str], ExceptionDirective], list[str]]:
    directives: dict[tuple[int, str], ExceptionDirective] = {}
    errors: list[str] = []
    for index, line in enumerate(raw_lines, start=1):
        if EXCEPTION_MARKER not in line:
            continue
        target = next((number for number in range(index + 1, len(raw_lines) + 1) if raw_lines[number - 1].strip()), None)
        if target is None or (index not in selected and target not in selected):
            continue
        match = EXCEPTION_RE.search(line)
        if not match:
            errors.append(f"line {index}: malformed learner-language exception")
            continue
        rule_id, reason, explanation = (value.strip() for value in match.groups())
        if rule_id not in known_rules:
            errors.append(f"line {index}: exception names unknown rule {rule_id}")
            continue
        if len(reason) < 8 or len(explanation) < 3:
            errors.append(f"line {index}: exception requires a specific reason and explanation location")
            continue
        key = (target, rule_id)
        if key in directives:
            errors.append(f"line {index}: duplicate exception for {rule_id} on target line {target}")
            continue
        directives[key] = ExceptionDirective(rule_id, index, target, reason, explanation)
    return directives, errors


def _advisories(path: str, line_number: int, fragment: str, configuration: Configuration) -> list[Finding]:
    findings: list[Finding] = []
    for sentence in SENTENCE_RE.findall(fragment):
        if len(WORD_RE.findall(sentence)) > configuration.sentence_word_limit:
            findings.append(Finding("advisory.long-sentence", "advisory", path, line_number, "Consider whether this sentence can be made easier to scan."))
            break
    lowered = fragment.casefold()
    for term in configuration.possible_jargon:
        if re.search(rf"\b{re.escape(term)}\w*\b", lowered):
            findings.append(Finding("advisory.possible-jargon", "advisory", path, line_number, f"Check whether '{term}' is necessary or needs a nearby explanation."))
            break
    acronyms = sorted({item for item in ACRONYM_RE.findall(fragment) if item not in configuration.acronym_allowlist})
    if acronyms:
        findings.append(Finding("advisory.possible-acronym", "advisory", path, line_number, f"Check whether {', '.join(acronyms)} needs expansion on first use."))
    return findings


def inspect_source(
    path: str, text: str, selected: set[int], configuration: Configuration
) -> tuple[list[Finding], list[str], int]:
    raw_lines = text.splitlines()
    cleaned_lines = _strip_comments(raw_lines)
    technical = _technical_record_lines(raw_lines, configuration.technical_record_labels)
    known = {rule.identifier for rule in configuration.blocking_rules}
    directives, errors = _directives(raw_lines, selected, known)
    used: set[tuple[int, str]] = set()
    findings: list[Finding] = []
    inspected = 0

    for line_number in sorted(number for number in selected if 1 <= number <= len(raw_lines)):
        if line_number in technical or "<code" in raw_lines[line_number - 1].casefold():
            continue
        fragments = _candidate_fragments(cleaned_lines[line_number - 1], configuration)
        if not fragments:
            continue
        inspected += 1
        for fragment in fragments:
            for rule in configuration.blocking_rules:
                if not rule.pattern.search(fragment):
                    continue
                key = (line_number, rule.identifier)
                if key in directives:
                    used.add(key)
                    continue
                findings.append(Finding(rule.identifier, "blocking", path, line_number, rule.message, rule.replacement))
            findings.extend(_advisories(path, line_number, fragment, configuration))

    for key, directive in directives.items():
        if key not in used:
            errors.append(
                f"line {directive.line}: exception for {directive.rule_id} is stale; "
                f"target line {directive.target_line} has no matching blocking occurrence"
            )
    unique = sorted(set(findings), key=lambda item: (item.path, item.line, item.severity, item.rule_id, item.message))
    return unique, errors, inspected


def run_check(
    root: Path, configuration: Configuration, *, base_ref: str | None, all_sources: bool
) -> dict[str, object]:
    raw_selection = all_owned_lines(root, configuration) if all_sources else changed_lines(root, base_ref)
    selection = {path: lines for path, lines in raw_selection.items() if owned_path(path, configuration)}
    findings: list[Finding] = []
    errors: list[str] = []
    inspected_regions = 0
    for path in sorted(selection):
        source = root / path
        if not source.is_file():
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exception:
            errors.append(f"{path}: unable to read UTF-8 source: {exception}")
            continue
        source_findings, source_errors, source_regions = inspect_source(path, text, selection[path], configuration)
        findings.extend(source_findings)
        errors.extend(f"{path}:{message}" for message in source_errors)
        inspected_regions += source_regions

    findings.sort(key=lambda item: (item.path, item.line, item.severity, item.rule_id, item.message))
    blocking = sum(item.severity == "blocking" for item in findings)
    advisory = sum(item.severity == "advisory" for item in findings)
    return {
        "schema_version": REPORT_SCHEMA,
        "status": "error" if errors else ("blocked" if blocking else "passed"),
        "selection": "all" if all_sources else ("base-ref" if base_ref else "changed"),
        "base_ref": base_ref,
        "selected_files": len(selection),
        "inspected_regions": inspected_regions,
        "blocking_count": blocking,
        "advisory_count": advisory,
        "findings": [asdict(item) for item in findings],
        "errors": sorted(errors),
    }


def _human(report: dict[str, object]) -> str:
    lines: list[str] = []
    for error in report["errors"]:
        lines.append(f"ERROR {error}")
    for finding in report["findings"]:
        replacement = f" Prefer: {finding['replacement']}" if finding.get("replacement") else ""
        lines.append(
            f"{finding['severity'].upper()} {finding['path']}:{finding['line']} "
            f"[{finding['rule_id']}] {finding['message']}{replacement}"
        )
    lines.append(
        "Learner-language check "
        f"{report['status']}: {report['inspected_regions']} region(s) in "
        f"{report['selected_files']} file(s); {report['blocking_count']} blocking, "
        f"{report['advisory_count']} advisory."
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", help="Git revision used to select changed learner-facing lines")
    parser.add_argument("--all", action="store_true", dest="all_sources", help="check all owned learner-facing source")
    parser.add_argument("--json", action="store_true", help="emit the stable machine-readable result")
    parser.add_argument("--root", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--config", default=DEFAULT_CONFIG, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.all_sources and args.base_ref:
        parser.error("--all and --base-ref are mutually exclusive")
    try:
        root = repository_root(args.root) if args.root else repository_root()
        configuration = load_configuration(root / args.config)
        report = run_check(root, configuration, base_ref=args.base_ref, all_sources=args.all_sources)
    except CheckError as exception:
        report = {
            "schema_version": REPORT_SCHEMA,
            "status": "error",
            "selection": "all" if args.all_sources else ("base-ref" if args.base_ref else "changed"),
            "base_ref": args.base_ref,
            "selected_files": 0,
            "inspected_regions": 0,
            "blocking_count": 0,
            "advisory_count": 0,
            "findings": [],
            "errors": [str(exception)],
        }
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else _human(report))
    if report["status"] == "error":
        return 2
    return 1 if report["blocking_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
