---
name: security-checks
description: Coordinate security review of code changes and interpret results from approved SAST, dependency, secret, and container scanners.
---

# Security Checks

## Goal
Identify and explain security risks using evidence from source code and approved scanners. Reuse deterministic tools rather than treating AI as a vulnerability scanner.

## Workflow
1. Confirm the scope: changed files, application type, build tool, deployment model, and available scanner outputs.
2. Identify existing security tooling before recommending new tools. Prefer the organization's approved GitLab security scanning, Semgrep, OWASP Dependency-Check, secret scanning, container scanning, and dependency review configurations.
3. If scan reports are supplied, parse severity, rule/CVE, affected dependency or source location, reachability/context if known, and remediation advice.
4. Inspect changed code for common risks: injection, broken authorization, insecure deserialization, path traversal, SSRF, XSS, CSRF, insecure crypto, unsafe file handling, secrets in source, sensitive data exposure, unsafe redirects, and weak input validation.
5. For each concern, distinguish confirmed vulnerability, scanner finding requiring triage, and potential risk requiring validation.
6. Prioritize by severity, exploitability, exposure, and business impact. Do not invent CVSS scores or claim exploitability without evidence.
7. Suggest concrete fixes and tests. Explain false-positive indicators without dismissing a finding solely because AI suspects one.
8. State which scanners actually ran, their versions if known, and what was not scanned.

For example scanner commands and GitLab integration notes, see [scanner commands](./references/scanner-commands.md).

## Output
- Summary and scope
- Scanners and reports reviewed (or explicitly “not run”)
- Findings sorted by severity with evidence, impact, and remediation
- False-positive / validation notes
- Gaps and next actions

## Safety
- Never print secret values. Redact credentials from output.
- Do not exploit systems, exfiltrate data, or run destructive tests.
- Do not upload code, binaries, logs, or scanner reports to external services unless authorized.
- AI recommendations do not replace security gates, code review, or compliance controls.
