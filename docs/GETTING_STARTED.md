# Getting started

## VS Code setup

1. Install and sign in to GitHub Copilot and enable Copilot Chat.
2. Install selected features into your project with `scripts/install.py`.
3. Open Copilot Chat in the target project.
4. Type `/` to view installed skills. Choose a skill, or enter its slash command, for example `/logging-advisor`.
5. Open the Agent picker to select installed custom agents such as **Log Analyzer**, **Code Reviewer**, **Documentation Assistant**, or **Security Reviewer**.

### Skills, prompts, and agents

- **Skill:** reusable task knowledge and workflow. It is the primary portable unit in this toolkit. A skill is a directory containing `SKILL.md` and may include helper scripts or examples.
- **Prompt file:** a named task template that you invoke manually. VS Code's current documentation says prompt files run in Local harness sessions. For Copilot harness sessions, use the related skill or agent.
- **Custom agent:** a role with focused instructions, such as a read-only Log Analyzer or Security Reviewer. Agents appear in the Agent picker.
- **MCP server:** a connection to an external tool or information source. Add one only if a workflow needs an external action or data source.

### Check installed files

A project using all features should contain a subset of:

```text
project/
├── .github/
│   ├── agents/
│   ├── prompts/
│   └── skills/
└── .gitlab/
    └── duo/
        └── mr-review-instructions.yaml
```

### Example usage

- `/logging-advisor Review the currently open Java service class. Suggest logging only; do not edit it.`
- `/log-analyzer Analyze the redacted log file at logs/app-redacted.log and correlate errors with relevant source code.`
- `/occ-postman-generator Inspect the custom OCC controllers under the current project and propose a Postman collection. Do not invent endpoints.`
- `/drawio-diagram-generator Create an editable component diagram for the current service architecture.`
- `/documentation-confluence Draft an architecture page from the current source code and README. Do not publish it.`
- `/worklog-generator Turn today's verified Git activity and my notes into a concise worklog. Ask me for actual hours.`
- `/code-review Review my current branch changes for defects, security, performance, and regressions. Do not modify files.`
- `/security-checks Review scanner outputs and changed files for security risks. Do not claim a scan ran unless it did.`

## Use the helper scripts

Run from the toolkit root or from a copied target project.

### Redact a log file

```bash
python .github/skills/log-analyzer/scripts/redact_logs.py application.log --output application.redacted.log
```

Without `--output`, the redacted content is written to standard output. The original file is never modified in place. Then summarize recurring patterns:

```bash
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

See `integrations/mcp/README.md`. MCP configuration may be user-level or workspace-level. Prefer user-level configuration for personal use; use a repository-shared configuration only after checking your organization's policy and the MCP server's permissions.
