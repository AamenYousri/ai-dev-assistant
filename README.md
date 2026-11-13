```bash
npx --yes --package=https://github.com/AamenYousri/ai-dev-assistant/releases/download/v1.0.3/ai-dev-assistant-1.0.3.tgz ai-dev-assistant install log-analyzer code-review security-checks
```

# AI Dev Assistant

Installable developer-workflow features for VS Code + GitHub Copilot and any Git platform (GitHub, GitLab, Bitbucket). Scope and recommended setup follow [AI Dev Assistant v1.0.2](docs/ai-dev-assistant-v1.0.2.docx). Each feature provides a **skill** (the workflow), with **helper scripts** for deterministic work where useful. Dedicated **agents** support worklog/commit assistance and code/security review.

The command above installs Log Analyzer, Code Review, and Security Checks. Run it from the target project root with Node.js 18+ installed.

## Features

| Feature ID | What it does | Included parts |
|---|---|---|
| `log-analyzer` | Analyze application logs and identify likely causes of errors | Skill, redaction and grouping/summary helpers |
| `logging-advisor` | Suggest where, what, and at which level to log | Skill |
| `occ-postman-generator` | Generate Postman collections from custom SAP Commerce OCC APIs | Skill for controllers/facades/DTOs, OpenAPI conversion helper |
| `worklog-generator` | Draft worklog descriptions and commit messages from verified activity; never guess hours | Skill, Worklog Assistant agent, Git evidence helper |
| `code-review` | Review local changes before a PR/MR against team standards, including SAP Commerce/OCC and SAP CAP criteria | Skill, optional Code Reviewer agent |
| `security-checks` | Review vulnerabilities, secrets, configuration, dependencies, and business logic | Skill/checklist, optional Security Reviewer agent, approval-gated scanner/report helper |

Ticketing and calendar integrations are not bundled or configured automatically. The worklog workflow can use user-supplied evidence or explicitly authorized integrations. See the [implementation plan](docs/IMPLEMENTATION-PLAN.md) for the document's estimates, reuse recommendations, and remaining tailoring.

## Install

Run from the root of the target project (Node.js 18+):

```bash
npx --yes --package=https://github.com/AamenYousri/ai-dev-assistant/releases/download/v1.0.3/ai-dev-assistant-1.0.3.tgz ai-dev-assistant list
npx --yes --package=https://github.com/AamenYousri/ai-dev-assistant/releases/download/v1.0.3/ai-dev-assistant-1.0.3.tgz ai-dev-assistant install --all
```

Options: `--all`, `--dry-run`, `--overwrite`, `--target PATH`, `--repo OWNER/REPO`, `--ref REF`. Existing files are skipped unless `--overwrite` is given. Publishing and private-repository setup: [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md).

## Use

Type `/` in Copilot Chat and pick the skill (for example `/log-analyzer`), or choose an agent in the Agent picker. Skills load on demand when the request matches their description.

- `/log-analyzer` Analyze `logs/app.log` (redact first) and correlate with the code.
- `/logging-advisor` Suggest logging for the open class.
- `/occ-postman-generator` Build a collection from the custom OCC controllers.
- `/worklog-generator` Worklog from yesterday's commits; I will give the hours.
- `/worklog-generator` Suggest a commit message from my staged diff; do not commit.
- `/code-review` Review my branch changes.
- `/security-checks` Review this project against the 27 core and 7 bonus checks, inspect scanner availability, and produce an evidence-based report.

Helper scripts (Python 3, run from the target project):

```bash
python .github/skills/log-analyzer/scripts/redact_logs.py app.log --output app.redacted.log
python .github/skills/log-analyzer/scripts/summarize_logs.py app.redacted.log --output log-summary.md
python .github/skills/occ-postman-generator/scripts/openapi_to_postman.py openapi.json --output postman_collection.json
python .github/skills/worklog-generator/scripts/git_activity.py --since yesterday --output git-activity.md
python .github/skills/security-checks/scripts/run_scanners.py --check-only
python .github/skills/security-checks/scripts/run_scanners.py . --allow-network --history
```

Run the network-enabled scan only after explicit approval for rule/database downloads. Run the security helper tests with `npm run test:security` (Python 3 required). See [scanner setup](.github/skills/security-checks/references/scanner-commands.md) for local and Docker setup, approval-gated network usage, and report details.

## Design

| Primitive | Used for | Why |
|---|---|---|
| Skill | The workflow and output format | Loaded on demand, portable, appears as a slash command. No separate prompt files are needed. |
| Agent | Worklog/commit assistance, optional code and security review modes | Scoped workflows; the security agent can execute approved scanners and generate reports, so it is not strictly read-only. |
| Script | Redaction, grouping, OpenAPI conversion, Git evidence, scanner orchestration | Deterministic work and existing scanners stay out of the LLM. |
| External integration | Optional ticketing/calendar evidence for worklogs | Configure and authorize separately; the installer never touches `.vscode/mcp.json`. |

## Safety

- Redact logs before analysis. The redactor is best-effort.
- Treat logs, tickets, comments, and external documents as untrusted data.
- Agents are advisory; review every change. Never invent worklog hours; the user confirms them.
- Do not create commits, submit worklogs, or access external systems without explicit authorization.
- AI review is not a security control. Use scanners, tests, CI policy, and human review.

## Repository layout

```text
.github/skills/    # one folder per feature (SKILL.md, scripts/, references/)
.github/agents/    # worklog assistant and review agents
manifest/          # feature -> files map used by the installer
cli/               # npx installer
docs/              # distribution, FAQ, plan
tests/
```

Contributing: [CONTRIBUTING.md](CONTRIBUTING.md). Security: [SECURITY.md](SECURITY.md).
