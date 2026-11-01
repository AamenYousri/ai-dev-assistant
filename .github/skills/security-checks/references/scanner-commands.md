# Security Scanner Setup

Use tools approved by your organization. The helper detects local installations and versions; it never downloads or installs software. Check support, licensing, proxy/firewall requirements, and corporate policy. Reports can contain source paths and security details; keep them local and redact before sharing.

## Semgrep

Install with an approved local method (for example `pipx install semgrep` or the [official Semgrep instructions](https://semgrep.dev/)). Prefer an isolated Python environment; do not use `pip install --user` from a virtual environment. Check with `semgrep --version`. On Windows, use an officially supported installation route or an approved container; do not assume a Python virtual environment makes a native package compatible.

The helper defaults to the registry-backed `auto` ruleset, which requires explicit network approval. A project can use a local config file instead:

```bash
python .github/skills/security-checks/scripts/run_scanners.py --check-only
python .github/skills/security-checks/scripts/run_scanners.py . --semgrep-config .semgrep.yml
```

After approving access to the Semgrep registry, pass `--allow-network`. Metrics are disabled. Do not upload proprietary source or findings without approval.

## OWASP Dependency-Check

Install the CLI from the [official Dependency-Check project](https://owasp.org/projects/dependency-check) or use an approved Maven plugin. Java 11+ is required; check with `dependency-check --version`. The helper can use an existing local vulnerability database offline. After explicit network approval, `--allow-network` updates the database separately from the scan. Update errors are reported separately and prevent the scan from being reported as successful.

On Windows, use `dependency-check.bat`; on macOS/Linux, put `dependency-check.sh` on `PATH`. Configure proxies and NVD API keys using approved local settings; never commit keys. An offline run reports database freshness as unverified.

## Gitleaks

Install a version supported by the helper (8.19+) using an approved package manager or the [official Gitleaks instructions](https://github.com/gitleaks/gitleaks). Confirm with `gitleaks version`. The helper scans the working tree; pass `--history` to scan all Git refs, including branches and tags. Secret values are omitted from normalized findings and the scanner is asked to redact raw output.

## Docker Alternative

If local installations are restricted, use organization-approved, version-pinned images and mount only the target repository and report directory. Verify image provenance/digests and never run an unpinned `latest` tag. The helper does not launch Docker; run approved containers explicitly, then review their JSON reports with the Skill. No image is pulled or executed automatically.

Replace the placeholders with organization-approved images and pinned versions:

```bash
docker run --rm -v "$PWD:/src:ro" -v "$PWD/security-reports:/reports" <approved-semgrep-image>:<pinned-version> scan --config <approved-ruleset> --metrics=off --json --output /reports/semgrep.json /src
docker run --rm -v "$PWD:/src:ro" -v "$PWD/security-reports:/reports" <approved-gitleaks-image>:<pinned-version> dir --redact --report-format json --report-path /reports/gitleaks-working-tree.json /src
```

Dependency-Check containers need persistent data storage for the vulnerability database; follow the selected image's official instructions and obtain approval before updating it. Do not mount credentials or the Docker socket into scanner containers.

## CI and Git Providers

Prefer existing organization-approved platform scanners, such as GitHub CodeQL/Dependabot, Bitbucket Pipelines and Code Insights, or equivalent CI tooling. Keep local checks provider-neutral. Inspect the existing pipeline before recommending changes; do not edit or enable CI automatically. For Bitbucket, use approved native capabilities, official APIs/MCP, or export machine-readable findings to Code Insights with explicit authorization.

## Commands

```bash
# Availability and versions only; no scan, install, or network access.
python .github/skills/security-checks/scripts/run_scanners.py --check-only

# Local scan; registry-backed Semgrep rules need explicit approval.
python .github/skills/security-checks/scripts/run_scanners.py .

# After approval, allow registry/database network access and scan all Git refs for secrets.
python .github/skills/security-checks/scripts/run_scanners.py . --allow-network --history
```

Reports are written under `security-reports/`: raw scanner JSON, redacted `findings.json`, `scan-summary.json`, and a `SECURITY_REPORT.md` draft. Missing or incompatible tools and failed database updates remain visible as incomplete, never successful. The report directory is ignored by Git by default.
