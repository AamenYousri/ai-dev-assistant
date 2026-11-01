#!/usr/bin/env python3
"""Check approved local scanners and create redacted machine-readable reports.

No scanner is installed or downloaded by this helper. Network access for Semgrep
registry rules and Dependency-Check database updates requires --allow-network.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SECRET_PATTERNS = (
    (re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)((?:password|passwd|secret|token|api[_-]?key)\s*[:=]\s*)[^\s,;\"']+"), r"\1[REDACTED]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), "[REDACTED]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED]"),
)


def mask_text(value):
    text = str(value or "")
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def parse_version(text):
    match = re.search(r"(?<!\d)(\d+)\.(\d+)(?:\.(\d+))?", text or "")
    return tuple(int(part or 0) for part in match.groups()) if match else None


def command_version(executable, args):
    try:
        command = [executable, *args]
        if os.name == "nt" and executable.lower().endswith(".bat"):
            command = [os.environ.get("COMSPEC", "cmd.exe"), "/c", *command]
        result = subprocess.run(command, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, mask_text(exc)
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode != 0:
        return None, mask_text(output[-500:] or f"version command exited {result.returncode}")
    return output.splitlines()[0] if output else "unknown", None


def java_major_version():
    executable = shutil.which("java")
    if not executable:
        return None, "Java is not installed or is not on PATH."
    version, error = command_version(executable, ["-version"])
    if error:
        return None, error
    found = re.search(r'"?(\d+)(?:\.(\d+))?', version or "")
    if not found:
        return None, f"Could not parse Java version: {mask_text(version)}"
    major = int(found.group(1))
    return (int(found.group(2)) if major == 1 and found.group(2) else major), None


def discover_scanners():
    candidates = {
        "semgrep": ("semgrep", "semgrep.exe"),
        "dependency-check": (("dependency-check.bat", "dependency-check") if os.name == "nt" else ("dependency-check.sh", "dependency-check")),
        "gitleaks": ("gitleaks", "gitleaks.exe"),
    }
    discovered = {}
    for name, names in candidates.items():
        executable = next((shutil.which(candidate) for candidate in names if shutil.which(candidate)), None)
        if not executable:
            discovered[name] = {"status": "missing", "reason": "Not found on PATH; no installation was attempted."}
            continue
        version_args = ["version"] if name == "gitleaks" else ["--version"]
        version, error = command_version(executable, version_args)
        if error:
            discovered[name] = {"status": "incompatible", "executable": executable, "reason": error}
            continue
        parsed = parse_version(version)
        info = {"status": "available", "executable": executable, "version": version}
        if parsed is None:
            info.update(status="incompatible", reason="Could not determine a numeric version.")
        elif name == "gitleaks" and parsed < (8, 19, 0):
            info.update(status="incompatible", reason="Version 8.19 or later is required for directory and Git-history scanning.")
        elif name == "dependency-check":
            java_major, java_error = java_major_version()
            info["java_major"] = java_major
            if java_error:
                info.update(status="incompatible", reason=java_error)
            elif java_major < 11:
                info.update(status="incompatible", reason=f"Java 11 or later is required; found Java {java_major}.")
        discovered[name] = info
    return discovered


def report_path(out, filename):
    out.mkdir(parents=True, exist_ok=True)
    return out / filename


def load_report(path, expected_type):
    try:
        with path.open(encoding="utf-8") as report_file:
            data = json.load(report_file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid or incomplete JSON report {path.name}: {exc}") from exc
    if not isinstance(data, expected_type):
        raise ValueError(f"Unexpected JSON structure in {path.name}.")
    return data


def redact_json(value):
    if isinstance(value, dict):
        return {key: redact_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_json(item) for item in value]
    if isinstance(value, str):
        return mask_text(value)
    return value


def finding(source, title, severity, category, location, evidence, scanner_id=None, cve=None, recommendation=None):
    return {
        "title": mask_text(title) or "Security finding",
        "severity": (mask_text(severity) or "Unknown").upper(),
        "category": mask_text(category) or "Uncategorized",
        "location": mask_text(location) or "Not provided by scanner",
        "evidence": mask_text(evidence),
        "scanner_id": mask_text(scanner_id),
        "cve": mask_text(cve),
        "recommendation": mask_text(recommendation),
        "sources": [source],
    }


def semgrep_findings(report):
    results = report.get("results")
    if not isinstance(results, list):
        raise ValueError("Semgrep report is missing its results array.")
    findings = []
    for item in results:
        if not isinstance(item, dict):
            raise ValueError("Semgrep report contains a malformed result entry.")
        extra = item.get("extra") if isinstance(item.get("extra"), dict) else {}
        start = item.get("start") if isinstance(item.get("start"), dict) else {}
        metadata = extra.get("metadata") if isinstance(extra.get("metadata"), dict) else {}
        cwes = metadata.get("cwe", [])
        category = ", ".join(cwes) if isinstance(cwes, list) else "SAST"
        findings.append(finding("Semgrep", extra.get("message"), extra.get("severity"), category,
                                 f"{item.get('path', '')}:{start.get('line', '?')}", extra.get("message"),
                                 item.get("check_id"), recommendation=metadata.get("fix")))
    return findings


def dependency_check_findings(report):
    dependencies = report.get("dependencies")
    if not isinstance(dependencies, list):
        raise ValueError("Dependency-Check report is missing its dependencies array.")
    findings = []
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            raise ValueError("Dependency-Check report contains a malformed dependency entry.")
        vulnerabilities = dependency.get("vulnerabilities") or []
        if not isinstance(vulnerabilities, list):
            raise ValueError("Dependency-Check report contains a malformed vulnerabilities list.")
        for vulnerability in vulnerabilities:
            if not isinstance(vulnerability, dict):
                raise ValueError("Dependency-Check report contains a malformed vulnerability entry.")
            cve = vulnerability.get("name") or vulnerability.get("source")
            package = dependency.get("fileName") or dependency.get("packages") or "Dependency"
            findings.append(finding("OWASP Dependency-Check", vulnerability.get("description") or cve,
                                     vulnerability.get("severity"), "Vulnerable dependency", str(package),
                                     vulnerability.get("description"), cve=cve))
    return findings


def gitleaks_findings(report, source):
    if not isinstance(report, list):
        raise ValueError("Gitleaks report must be a JSON array.")
    findings = []
    for item in report:
        if not isinstance(item, dict):
            raise ValueError("Gitleaks report contains a malformed finding entry.")
        findings.append(finding(source, item.get("Description") or item.get("RuleID"), "HIGH", "Exposed secret",
                                f"{item.get('File', '')}:{item.get('StartLine', '?')}",
                                "Secret detected; value intentionally omitted.", item.get("RuleID")))
    return findings


def deduplicate_findings(findings):
    unique = {}
    for item in findings:
        cve = item.get("cve")
        identity = f"cve:{cve}|{item.get('location', '')}" if cve else "|".join((item.get("scanner_id", ""), item.get("location", ""), item.get("title", "")))
        if identity not in unique:
            unique[identity] = item
        else:
            for source in item.get("sources", []):
                if source not in unique[identity]["sources"]:
                    unique[identity]["sources"].append(source)
    return list(unique.values())


def run_process(command, timeout):
    try:
        if os.name == "nt" and command[0].lower().endswith(".bat"):
            command = [os.environ.get("COMSPEC", "cmd.exe"), "/c", *command]
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return exc


def execute_scanner(name, info, target, out, args):
    if info.get("status") != "available":
        return {**info, "scan_status": "not_run"}, []
    if name == "semgrep" and not args.allow_network and not Path(args.semgrep_config).is_file():
        return {**info, "scan_status": "needs_approval", "reason": "Semgrep registry rules require network access; rerun with --allow-network after approval."}, []
    database_update = "not_applicable"
    if name == "dependency-check" and args.allow_network:
        update = run_process([info["executable"], "--updateonly"], args.timeout)
        if isinstance(update, Exception) or update.returncode != 0:
            return {**info, "scan_status": "failed", "database_update": "failed", "scan": "not_run",
                    "reason": "Dependency-Check database update failed; diagnostic output was not copied into the report."}, []
        database_update = "succeeded"
    elif name == "dependency-check":
        database_update = "not_attempted_offline"
    report_name = {"semgrep": "semgrep.json", "dependency-check": "dependency-check-report.json", "gitleaks": "gitleaks-working-tree.json"}[name]
    output = report_path(out, report_name)
    output.unlink(missing_ok=True)
    if name == "semgrep":
        command = [info["executable"], "scan", "--config", args.semgrep_config, "--metrics=off", "--json", "--output", str(output), target]
    elif name == "dependency-check":
        command = [info["executable"], "--noupdate", "--project", Path(target).name, "--scan", target, "--format", "JSON", "--out", str(out)]
    else:
        command = [info["executable"], "dir", "--redact", "--report-format", "json", "--report-path", str(output), target]
    process = run_process(command, args.timeout)
    if isinstance(process, Exception):
        return {**info, "scan_status": "failed", "database_update": database_update,
            "reason": "Scanner process failed or timed out; diagnostic output was not copied into the report."}, []
    try:
        report = load_report(output, list if name == "gitleaks" else dict)
        report = redact_json(report)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        findings = (semgrep_findings(report) if name == "semgrep" else
                    dependency_check_findings(report) if name == "dependency-check" else
                    gitleaks_findings(report, "Gitleaks working tree"))
    except ValueError as exc:
        return {**info, "scan_status": "failed", "database_update": database_update,
                "exit_code": process.returncode, "reason": mask_text(exc)}, []
    if process.returncode not in ({0, 1} if name == "gitleaks" else {0}):
        return {**info, "scan_status": "failed", "database_update": database_update,
                "exit_code": process.returncode, "reason": "Scanner exited unsuccessfully despite producing JSON."}, []
    if name == "gitleaks" and process.returncode == 1 and not findings:
        return {**info, "scan_status": "failed", "database_update": database_update,
                "exit_code": process.returncode, "reason": "Gitleaks returned its findings exit code but the report contained no findings."}, []
    result = {**info, "scan_status": "completed_with_findings" if findings else "completed",
              "database_update": database_update, "exit_code": process.returncode,
              "finding_count": len(findings), "report": report_name}
    return result, findings


def scan_gitleaks_history(info, target, out, timeout):
    if info.get("status") != "available":
        return {**info, "scan_status": "not_run"}, []
    if not (Path(target) / ".git").exists():
        return {**info, "scan_status": "not_run", "reason": "Target is not a Git working tree."}, []
    name = "gitleaks-history.json"
    output = report_path(out, name)
    command = [info["executable"], "git", "--redact", "--report-format", "json", "--report-path", str(output), "--log-opts=--all", target]
    process = run_process(command, timeout)
    if isinstance(process, Exception):
        return {**info, "scan_status": "failed", "reason": "Gitleaks history scan failed or timed out; diagnostic output was not copied into the report."}, []
    try:
        report = redact_json(load_report(output, list))
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        findings = gitleaks_findings(report, "Gitleaks Git history")
    except ValueError as exc:
        return {**info, "scan_status": "failed", "exit_code": process.returncode, "reason": mask_text(exc)}, []
    if process.returncode not in (0, 1) or (process.returncode == 1 and not findings):
        return {**info, "scan_status": "failed", "exit_code": process.returncode,
                "reason": "Gitleaks exited unsuccessfully or its findings exit code disagreed with its report."}, []
    result = {**info, "scan_status": "completed_with_findings" if findings else "completed",
              "exit_code": process.returncode, "finding_count": len(findings), "report": name}
    return result, findings


def write_report_draft(out, summary, findings):
    checklist = Path(__file__).resolve().parents[1] / "references" / "security-checklist.md"
    checks = re.findall(r"^### ((?:C\d{2}|B\d))\. (.+)$", checklist.read_text(encoding="utf-8"), re.MULTILINE)
    lines = [
        "# Security Report",
        "",
        "## 1. Executive Summary",
        f"- Status: **{summary.get('overall', 'incomplete').upper()}**",
        f"- Target: `{mask_text(summary.get('target', 'unknown'))}`",
        f"- Scanner findings requiring triage: {summary.get('finding_count', 0)}",
        "- This generated draft is not a complete security assessment; complete the checklist using project evidence.",
        "",
        "## 2. Project Security Context",
        "- Status: NEEDS MANUAL REVIEW; inspect the project architecture, technologies, trust boundaries, and sensitive data.",
        "",
        "## 3. Security Checks Performed",
        "- Automated scanner executions are summarized below. Application-specific checklist review is NOT RUN until evidence is added.",
        "",
        "## 4. Scanner Availability and Versions",
        "| Scanner | Availability | Version | Run status | Notes |",
        "|---|---|---|---|---|",
    ]
    for name, result in summary.get("scanners", {}).items():
        version = mask_text(result.get("version", "unknown"))
        reason = mask_text(result.get("reason", ""))
        lines.append(f"| {name} | {result.get('status', 'unknown')} | {version} | {result.get('scan_status', 'not_run')} | {reason} |")
    lines.extend(["", "## 5. Automated Scanner Results", f"- Overall scan status: **{summary.get('overall', 'incomplete')}**", f"- Finding count after deduplication: {summary.get('finding_count', 0)}", ""])
    lines.extend(["## 6. Findings Ordered by Severity", ""])
    if findings:
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        for item in sorted(findings, key=lambda finding_item: (severity_order.get(finding_item.get("severity", "").upper(), 4), finding_item.get("title", ""))):
            lines.extend([
                f"### NEEDS MANUAL REVIEW: {mask_text(item.get('title', 'Scanner finding'))}",
                f"- Severity: {mask_text(item.get('severity', 'Unknown'))}",
                f"- Category: {mask_text(item.get('category', 'Uncategorized'))}",
                f"- Location: `{mask_text(item.get('location', 'Not provided'))}`",
                f"- Evidence: {mask_text(item.get('evidence', 'No evidence supplied'))}",
                f"- Source: {', '.join(item.get('sources', []))}",
                f"- Recommendation: {mask_text(item.get('recommendation') or 'Triage with source context; do not infer exploitability from this scanner result alone.')}",
                "- Exploitation scenario and validation: NOT RUN; add only after manual review.",
                "",
            ])
    else:
        lines.append("No scanner findings were collected. This is not proof that the application is secure.\n")
    failed_scanners = [name for name, result in summary.get("scanners", {}).items() if result.get("scan_status") == "failed"]
    lines.extend([
        "## 7. Recommendations and Suggested Fixes",
        "- Triage each scanner finding and complete applicable checklist reviews before prioritizing fixes.",
        "",
        "## 8. Passed Checks and Evidence",
        "- None recorded. No check is marked PASS without explicit supporting evidence.",
        "",
        "## 9. Failed Checks",
        "- No application checklist check has been classified as FAIL by scanner output alone.",
        "",
        "## 10. Not Applicable Checks",
        "- None classified. Add project-specific reasons after reviewing applicability.",
        "",
        "## 11. Checks Not Performed",
        "| ID | Check | Status | Evidence / reason |",
        "|---|---|---|---|",
    ])
    if failed_scanners:
        failed_section = lines.index("## 9. Failed Checks") + 1
        lines[failed_section:failed_section] = [f"- Scanner execution failed: {name}; see the scanner table above." for name in failed_scanners]
    lines.extend(f"| {check_id} | {title} | NOT RUN | Review required |" for check_id, title in checks)
    lines.extend([
        "",
        "## 12. Manual Actions Required",
        "- Verify external identity, hosting, network, DNS/email, backup, account, CI, and billing controls with their owners.",
        "- Confirm Dependency-Check database freshness when `database_update` is `not_attempted_offline`.",
        "",
        "## 13. Validation and Retest Results",
        "- No application fixes or regression tests are represented by this generated draft.",
        "- Add commands, versions, exit statuses, evidence, and resolved/unresolved findings after retesting.",
        "",
    ])
    report_path(out, "SECURITY_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def overall_status(scanner_results, check_only=False):
    if check_only:
        return "availability_checked"
    statuses = [item.get("scan_status", "not_run") for item in scanner_results.values()]
    offline_database = any(item.get("database_update") == "not_attempted_offline" for item in scanner_results.values())
    if any(status == "failed" for status in statuses):
        return "failed"
    if offline_database or any(status in ("not_run", "needs_approval") for status in statuses):
        return "incomplete"
    return "completed"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--out", default="security-reports")
    parser.add_argument("--check-only", action="store_true", help="report versions and prerequisites without scanning")
    parser.add_argument("--allow-network", action="store_true", help="authorize Semgrep registry access and Dependency-Check database updates")
    parser.add_argument("--semgrep-config", default="auto", help="Semgrep ruleset name or local configuration path")
    parser.add_argument("--history", action="store_true", help="scan all Git refs (branches and tags) with Gitleaks")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args(argv)
    target = str(Path(args.target).resolve())
    out = Path(args.out).resolve()
    availability = discover_scanners()
    summary = {"generated_at": datetime.now(timezone.utc).isoformat(), "target": target,
               "network_authorized": args.allow_network, "scanners": {}}
    findings = []
    for name, info in availability.items():
        if args.check_only:
            summary["scanners"][name] = {**info, "scan_status": "not_run"}
        else:
            result, detected = execute_scanner(name, info, target, out, args)
            summary["scanners"][name] = result
            findings.extend(detected)
    if not args.check_only and args.history:
        result, detected = scan_gitleaks_history(availability["gitleaks"], target, out, args.timeout)
        summary["scanners"]["gitleaks_history"] = result
        findings.extend(detected)
    findings = deduplicate_findings(findings)
    summary["finding_count"] = len(findings)
    statuses = [item["scan_status"] for item in summary["scanners"].values()]
    summary["overall"] = overall_status(summary["scanners"], args.check_only)
    if not args.check_only:
        report_path(out, "findings.json").write_text(json.dumps({"findings": findings}, indent=2), encoding="utf-8")
        write_report_draft(out, summary, findings)
    report_path(out, "scan-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if any(status == "failed" for status in statuses):
        return 2
    if args.check_only:
        return 1 if any(info.get("status") != "available" for info in availability.values()) else 0
    return 1 if summary["overall"] == "incomplete" else 0


if __name__ == "__main__":
    sys.exit(main())
