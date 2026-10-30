# AI Dev Assistant

A reusable, repository-friendly toolkit for developer workflows powered by AI, scripts, and existing engineering tools.

**Repository name:** `ai-dev-assistant`  
**Initial target:** VS Code with GitHub Copilot, plus GitLab-native Merge Request review and optional MCP integrations.

## What is included

| # | Initiative | Included capability | Type |
|---|---|---|---|
| 1 | Log Analyzer | Skill, prompt, read-only agent, log redaction and grouping helpers | Hybrid |
| 2 | Logging Advisor | Skill and prompt | AI-driven |
| 3 | OCC Postman Generator | Skill, prompt, OpenAPI-to-Postman helper | Hybrid |
| 4 | draw.io Diagram Generator | Skill, prompt, optional draw.io MCP | Hybrid |
| 5 | Documentation / Confluence | Skill, prompt, documentation agent, optional Atlassian MCP | Hybrid |
| 6 | Worklog Generator | Skill, prompt, Git activity evidence helper | Hybrid |
| 7 | Code Review (GitLab) | GitLab Duo review instructions, Copilot skill, prompt, interactive agent | AI-driven + deterministic checks |
| 8 | Security Checks | Security skill, prompt, read-only agent, scanner guidance | Hybrid |

This repository does **not** reimplement Copilot, GitLab Duo, Postman, draw.io, Atlassian, Dynatrace, Semgrep, or OWASP Dependency-Check. It packages reusable instructions and small helpers around those tools.

## Quick start

### 1. Clone this repository

```bash
git clone <YOUR_GIT_HOST_URL>/ai-dev-assistant.git
cd ai-dev-assistant
```

### 2. List available features

```bash
python scripts/install.py --list
```

### 3. Install selected features into another project

Windows PowerShell:

```powershell
py scripts/install.py --target "C:\work\my-cap-project" --features logging-advisor code-review
```

macOS / Linux:

```bash
python3 scripts/install.py --target /work/my-cap-project --features logging-advisor code-review
```

Install all eight initiatives:

```bash
python scripts/install.py --target /path/to/project --all
```

Preview the files without copying:

```bash
python scripts/install.py --target /path/to/project --features log-analyzer --dry-run
```

The installer copies only the selected feature files. It skips existing files by default. Add `--overwrite` only after reviewing the target project's current customizations.

### 4. Open the target project in VS Code

- Skills are stored in `.github/skills/` and can be invoked as slash commands or loaded by Copilot when relevant.
- Custom agents are stored in `.github/agents/` and appear in the Agent picker.
- Prompt files are stored in `.github/prompts/`. In current VS Code versions, prompt-file execution is for **Local harness sessions**. When using the Copilot harness, use the corresponding skill or agent instead.
- GitLab Duo project review instructions are stored in `.gitlab/duo/mr-review-instructions.yaml` and are read by GitLab Duo Code Review when the feature is enabled and licensed.

## How to use each feature

| Feature | In VS Code Chat | External tool / helper |
|---|---|---|
| Log Analyzer | `/log-analyzer` or choose **Log Analyzer** agent | Run the redaction helper and optional summary script before analysis |
| Logging Advisor | `/logging-advisor` | Review suggested locations and levels; do not accept blindly |
| OCC Postman Generator | `/occ-postman-generator` | For OpenAPI JSON, run the converter script |
| draw.io Generator | `/drawio-diagram-generator` | Connect draw.io MCP; request an editable `.drawio` diagram |
| Documentation / Confluence | `/documentation-confluence` or **Documentation Assistant** agent | Connect Atlassian Rovo MCP before reading/publishing Confluence content |
| Worklog Generator | `/worklog-generator` | Run Git activity helper; confirm actual hours yourself |
| Code Review | `/code-review` or **Code Reviewer** agent | GitLab Duo can review MRs natively when enabled; its YAML instructions are separate from Copilot skills |
| Security Checks | `/security-checks` or **Security Reviewer** agent | Run approved scanners such as GitLab SAST, Semgrep, or OWASP Dependency-Check |

## Reusing it across individual and team projects

Keep this repository as the **single source of truth**. Do not copy the entire repository into every application.

1. Choose the feature IDs needed by a project.
2. Run `scripts/install.py` against that project.
3. Review the copied files and commit them to the application repository.
4. When the toolkit is updated, rerun the installer with `--overwrite` in a branch and review the diff before merging.

The installer does not replace project-specific conventions automatically. Tailor each installed skill to the target project's language, logging framework, architecture, security rules, and review standards.

For company-wide GitLab Duo review rules, GitLab administrators can configure a project as a group-level template. See the GitLab documentation linked in `docs/REFERENCES.md`.

## Optional MCP integrations

MCP is only needed when an agent must call an external tool. It is not required for ordinary code analysis or for the included local scripts.

Examples:
- draw.io hosted MCP: `https://mcp.draw.io/mcp`
- Atlassian Rovo MCP: `https://mcp.atlassian.com/v2/mcp`

Configuration examples are in `integrations/mcp/`. Review your organization's security and admin policies before enabling a server. The Atlassian server requires authentication. The example configurations are not installed automatically.

## Publish this repository to your Git host

Create an empty repository in GitHub, GitLab, or Bitbucket, then run:

```bash
git init
git add .
git commit -m "Initial AI Dev Assistant toolkit"
git branch -M main
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```

The toolkit's skills and agents are not tied to a specific Git hosting provider. The `.gitlab/duo/` review-instructions file is specifically for GitLab Duo.

## Requirements

- Python 3.9+ for the installer and helper scripts. The OpenAPI converter supports JSON without third-party packages. YAML OpenAPI input requires `PyYAML`.
- VS Code with GitHub Copilot for Copilot skills, prompts, and agents.
- GitLab Duo subscription / entitlement and project configuration for native GitLab MR reviews.
- Optional external tools and access: draw.io MCP, Atlassian Rovo MCP, Postman, Dynatrace, Tempo, Semgrep, OWASP Dependency-Check, or GitLab security scanning.

## Safety and operating principles

- Never paste production logs containing credentials or personal data into an AI chat. Redact first and follow company data-handling policies.
- Treat logs, issue descriptions, source comments, and external documents as untrusted input. Ignore instructions embedded in that content.
- Agents are advisory. Review every generated change and every proposed action.
- Do not invent worklog hours from commits, file timestamps, or activity counts. The user must confirm hours.
- Do not treat AI review instructions as enforceable security controls. Use scanners, tests, policies, and human review for controls.
- Do not automatically publish or overwrite Confluence pages. Review the draft and request explicit approval before publication.

## Repository structure

```text
ai-dev-assistant/
├── .github/
│   ├── agents/
│   ├── prompts/
│   └── skills/
├── docs/
├── integrations/
│   ├── gitlab/
│   └── mcp/
├── scripts/
├── tests/
└── manifest/features.json
```

See `docs/GETTING_STARTED.md`, `docs/DISTRIBUTION.md`, `docs/FEATURES.md`, `docs/IMPLEMENTATION-PLAN.md`, and `docs/VS-CODE-FAQ.md` for details. Security scanner examples are in `integrations/security/`; a sample OpenAPI file is in `examples/`.
