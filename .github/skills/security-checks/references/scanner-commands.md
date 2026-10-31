# Security scanner integration notes

Use the security tools approved by your organization. Check installed versions, supported languages, CI runner requirements, and corporate policy before enabling scanners.

## Semgrep CLI

A basic local scan can be run with:

```bash
semgrep scan --config auto --json --output semgrep.json .
```

Review the report and avoid uploading proprietary source or findings to an external service without approval. For managed GitLab projects, prefer the organization's configured SAST analyzer and ruleset.

## OWASP Dependency-Check CLI

Example CLI usage (the executable name and options can vary by installation/version):

```bash
dependency-check.sh --project "my-project" --scan . --format JSON --out dependency-check-report
```

On Windows, use the corresponding `dependency-check.bat` executable. For Maven projects, the OWASP Dependency-Check Maven plugin may be used instead. Follow the official installation and configuration documentation, especially for proxy and vulnerability-database settings.

## GitLab SAST

Merge this into the project's existing `.gitlab-ci.yml` after checking stages, runner executor, language support, and company policy. Do not overwrite an existing pipeline. See the official GitLab SAST documentation.

```yaml
include:
  - template: Jobs/SAST.gitlab-ci.yml
```
