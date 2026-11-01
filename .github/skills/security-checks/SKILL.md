---
name: security-checks
description: Perform evidence-based security reviews across application code, dependencies, configuration, and applicable infrastructure checks.
---

# Security Checks

## Goal
Review enterprise application security across code and project context. Use the criteria in [security checklist](./references/security-checklist.md), established scanners, and repeatable tests. Adapt checks to actual technologies; do not assume a check applies or claim external infrastructure was verified from source.

## Workflow
1. Establish scope and context from source, build files, deployment files, Git history, and user-provided facts. Record unknowns instead of guessing. Do not send code or reports to external services without authorization.
2. Check scanner availability before scanning with `python .github/skills/security-checks/scripts/run_scanners.py --check-only`. Report each scanner's version and whether it is available, missing, or incompatible. This helper never installs or downloads tools.
3. If a scanner is missing, explain local and Docker setup options in [scanner setup](./references/scanner-commands.md). Never install anything silently. Obtain explicit approval before installation, network access, database/rule downloads, or other consequential execution. A scan that needs network requires `--allow-network` after approval. Dependency-Check requires Java 11+.
4. After approval, run available scanners: `python .github/skills/security-checks/scripts/run_scanners.py . --history --allow-network`. Omit `--allow-network` only when Semgrep uses local rules and Dependency-Check can use its existing local database. Use `--semgrep-config PATH` for a project rules file. Gitleaks scans the working tree; `--history` scans all Git refs. The helper writes redacted reports and a `SECURITY_REPORT.md` draft under `security-reports/`.
5. Read `scan-summary.json` first. Treat `missing`, `incompatible`, `needs_approval`, `not_run`, malformed reports, nonzero execution failures, and offline/unverified vulnerability databases as incomplete, never as PASS. Interpret valid scanner findings; scanner alerts require triage, not automatic claims of exploitability.
6. Inspect relevant application code and tests against all applicable checks in the linked checklist. Include Java/Spring, SAP CAP, TypeScript/Angular/Fiori, SQL, APIs, and other technologies only when present. For external identity, hosting, email, backup, account, and network controls, provide manual verification instructions.
7. Consolidate duplicates by CVE or same rule and location. Mask credentials in evidence. For each finding state title, severity, category, location/endpoint, explanation, evidence, plausible exploitation scenario supported by evidence, recommended fix, validation, and source (scanner, manual review, or test). Never invent exposure, reachability, CVSS, or business impact.
8. Use only `PASS`, `FAIL`, `NEEDS MANUAL REVIEW`, `NOT APPLICABLE`, and `NOT RUN` in `SECURITY_REPORT.md`. A PASS requires cited evidence. Explain every NOT APPLICABLE decision. Leave uninspected checks NOT RUN. Default to reporting; get approval before modifying application source. After approval, fix one related issue at a time, add regression tests, then rerun the focused scanner/test.
9. State scanner versions, reports, database freshness/update outcome, checks not performed, manual actions, and retest outcome. The report draft marks checks NOT RUN until evidence is added.
For local and Docker setup examples and provider-neutral CI guidance, see [scanner commands](./references/scanner-commands.md).

## Output
- Generate or complete `security-reports/SECURITY_REPORT.md` with the executive summary, project context, checks performed, scanner versions/results, severity-ordered findings, passed/failed/NA/not-run checks, remediation, validation, and manual actions.
- Keep raw reports local, redacted, and out of version control. The repository ignores `security-reports/` by default.

## Safety
- Never print secret values. Scanner reports are masked on a best-effort basis; review before sharing.
- Do not exploit systems, exfiltrate data, or run destructive tests.
- Do not install tools, download scanner binaries/rules/databases, or upload code/reports unless explicitly authorized.
- AI recommendations do not replace security gates, code review, or compliance controls.
