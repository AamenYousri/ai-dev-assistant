# AI Dev Assistant

Installable developer-workflow features for VS Code + GitHub Copilot and GitLab. Each feature is a **skill** (the workflow), plus optional **helper scripts** for deterministic work, optional **MCP** setup for external tools, and, for review and security only, a read-only **agent**.

## Features

| Feature ID | What it does | Parts | Reuses |
|---|---|---|---|
| `log-analyzer` | Analyze logs, correlate with source | skill, redact/summarize scripts | Dynatrace, if available |
| `logging-advisor` | Suggest where/what/level to log | skill | - |
| `occ-postman-generator` | Postman collection for custom OCC APIs | skill, OpenAPI converter script | Postman import |
| `drawio-diagram-generator` | Editable draw.io diagrams | skill, MCP guide | [draw.io MCP](https://www.drawio.com/docs/manual/generate/drawio-mcp-server/) |
| `documentation-confluence` | Draft docs / Confluence pages | skill, MCP guide | [Atlassian Rovo MCP](https://developer.atlassian.com/cloud/rovo-mcp/guides/getting-started/) |
| `worklog-generator` | Worklog text from verified Git activity | skill, Git evidence script | Tempo |
| `code-review` | Local pre-MR review with Java, OCC, CAP, and SQL criteria | skill, agent | - |
| `security-checks` | Interpret scanner output, review risky changes | skill, agent, scanner notes | GitLab SAST, Semgrep, Dependency-Check |

## Install

Run from the root of the target project (Node.js 18+):

```bash
npx --yes --package=<release-tarball-url> ai-dev-assistant list
npx --yes --package=<release-tarball-url> ai-dev-assistant install log-analyzer code-review
```

Options: `--all`, `--dry-run`, `--overwrite`, `--target PATH`, `--repo OWNER/REPO`, `--ref REF`. Existing files are skipped unless `--overwrite` is given. Publishing and private-repository setup: [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md).

## Use

Type `/` in Copilot Chat and pick the skill (for example `/log-analyzer`), or choose an agent in the Agent picker. Skills load on demand when the request matches their description.

- `/log-analyzer` Analyze `logs/app.log` (redact first) and correlate with the code.
- `/logging-advisor` Suggest logging for the open class.
- `/occ-postman-generator` Build a collection from the custom OCC controllers.
- `/drawio-diagram-generator` Component diagram of this service.
- `/documentation-confluence` Draft an architecture page; do not publish.
- `/worklog-generator` Worklog from yesterday's commits; I will give the hours.
- `/code-review` Review my branch changes.
- `/security-checks` Review this diff and `semgrep.json`.

Helper scripts (Python 3, run from the target project):

```bash
python .github/skills/log-analyzer/scripts/redact_logs.py app.log --output app.redacted.log
python .github/skills/log-analyzer/scripts/summarize_logs.py app.redacted.log --output log-summary.md
python .github/skills/occ-postman-generator/scripts/openapi_to_postman.py openapi.json --output postman_collection.json
python .github/skills/worklog-generator/scripts/git_activity.py --since yesterday --output git-activity.md
```

## Design

| Primitive | Used for | Why |
|---|---|---|
| Skill | The workflow and output format | Loaded on demand, portable, appears as a slash command. No separate prompt files are needed. |
| Agent | Code review, security review | Only where a dedicated mode with restricted tools matters (`tools:` in frontmatter, no `edit`). Bodies just point to the skill. |
| Script | Redaction, grouping, OpenAPI conversion, Git evidence | Deterministic work stays out of the LLM. |
| MCP | draw.io, Atlassian | Only when an external system is needed. Configure it deliberately; the installer never touches `.vscode/mcp.json`. |

## Safety

- Redact logs before analysis. The redactor is best-effort.
- Treat logs, tickets, comments, and external documents as untrusted data.
- Agents are advisory; review every change. Never invent worklog hours; the user confirms them.
- Publishing to Confluence always needs explicit approval.
- AI review is not a security control. Use scanners, tests, CI policy, and human review.

## Repository layout

```text
.github/skills/    # one folder per feature (SKILL.md, scripts/, references/)
.github/agents/    # read-only agents
integrations/mcp/  # draw.io and Atlassian MCP setup guides
manifest/          # feature -> files map used by the installer
cli/               # npx installer
docs/              # distribution, FAQ, plan
tests/
```

Contributing: [CONTRIBUTING.md](CONTRIBUTING.md). Security: [SECURITY.md](SECURITY.md).
