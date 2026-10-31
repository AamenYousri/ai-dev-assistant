# Getting started

## Install into your project

The simplest option for developers is the GitHub Release installer. Open a terminal at the root of your existing project and run the npx command for the feature you need:

```bash
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install drawio-diagram-generator
```

This requires Node.js 18+ and npm/npx. It does not require Python or a manual clone. Run `ai-dev-assistant list` to see feature IDs. Add `--dry-run` to preview, `--overwrite` to replace existing files, or `--all` to install every feature. See [DISTRIBUTION.md](DISTRIBUTION.md) for how maintainers build and publish the CLI package and for private-repository authentication notes.

The original PowerShell and Python installers are also available for developers who have the toolkit source locally. See the repository README for their commands.

## VS Code setup

1. Install and sign in to GitHub Copilot and enable Copilot Chat.
2. Open Copilot Chat in the target project.
3. Type `/` to view installed skills. Choose a skill, or enter its slash command, for example `/logging-advisor`.
4. Open the Agent picker to select installed custom agents such as **Log Analyzer**, **Code Reviewer**, **Documentation Assistant**, or **Security Reviewer**.

## Skills, prompts, and agents

- **Skill:** reusable task knowledge and workflow. It is the primary portable unit in this toolkit. A skill is a directory containing `SKILL.md` and may include helper scripts or examples.
- **Prompt file:** a named task template that you invoke manually. VS Code's current documentation says prompt files run in Local harness sessions. For Copilot harness sessions, use the related skill or agent.
- **Custom agent:** a role with focused instructions, such as a read-only Log Analyzer or Security Reviewer. Agents appear in the Agent picker.
- **MCP server:** a connection to an external tool or information source. MCP setup guides are included with the corresponding feature; connecting the server still requires an explicit user action.

## Check installed files

A project using all features should contain a subset of:

```text
project/
├── .github/
│   ├── agents/
│   ├── prompts/
│   └── skills/
├── .gitlab/
│   └── duo/
└── docs/
    └── ai-dev-assistant/
```

## Example usage

- `/logging-advisor Review the currently open Java service class. Suggest logging only; do not edit it.`
- `/log-analyzer Analyze the redacted log file at logs/app-redacted.log and correlate errors with relevant source code.`
- `/occ-postman-generator Inspect the custom OCC controllers under the current project and propose a Postman collection. Do not invent endpoints.`
- `/drawio-diagram-generator Create an editable component diagram for the current service architecture.`
- `/documentation-confluence Draft an architecture page from the current source code and README. Do not publish it.`
- `/worklog-generator Turn today's verified Git activity and my notes into a concise worklog. Ask me for actual hours.`
- `/code-review Review my current branch changes for defects, security, performance, and regressions. Do not modify files.`
- `/security-checks Review scanner outputs and changed files for security risks. Do not claim a scan ran unless it did.`

## Use the helper scripts

Run these from the target project after installing the relevant feature. Python is required only for the helper scripts below, not for the npx installer.

### Redact a log file

```bash
python .github/skills/log-analyzer/scripts/redact_logs.py application.log --output application.redacted.log
python .github/skills/log-analyzer/scripts/summarize_logs.py application.redacted.log --output log-summary.md
```

### Convert an OpenAPI 3.x JSON file to a Postman collection

```bash
python .github/skills/occ-postman-generator/scripts/openapi_to_postman.py openapi.json --output postman_collection.json
```

YAML input is supported when `PyYAML` is installed:

```bash
python -m pip install PyYAML
python .github/skills/occ-postman-generator/scripts/openapi_to_postman.py openapi.yaml --output postman_collection.json
```

### Collect Git activity evidence

```bash
python .github/skills/worklog-generator/scripts/git_activity.py --since "yesterday" --until "now" --output git-activity.md
```

This script produces evidence only. It does not estimate or submit hours.

## Optional MCP setup

See `integrations/mcp/README.md`, or the feature-specific setup guide installed under `docs/ai-dev-assistant/`. MCP configuration may be user-level or workspace-level. Prefer user-level configuration for personal use; use a repository-shared configuration only after checking your organization's policy and the MCP server's permissions.
