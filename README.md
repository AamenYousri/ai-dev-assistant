# AI Dev Assistant

A reusable toolkit for developer workflows powered by AI, scripts, and existing engineering tools.

**Repository name:** `ai-dev-assistant`  
**Initial target:** VS Code with GitHub Copilot, plus GitLab-native Merge Request review and optional MCP integrations.

## What is included

| # | Initiative | Included capability | Type |
|---|---|---|---|
| 1 | Log Analyzer | Skill, prompt, read-only agent, log redaction and grouping helpers | Hybrid |
| 2 | Logging Advisor | Skill and prompt | AI-driven |
| 3 | OCC Postman Generator | Skill, prompt, OpenAPI-to-Postman helper | Hybrid |
| 4 | draw.io Diagram Generator | Skill, prompt, optional draw.io MCP setup | Hybrid |
| 5 | Documentation / Confluence | Skill, prompt, documentation agent, optional Atlassian MCP | Hybrid |
| 6 | Worklog Generator | Skill, prompt, Git activity evidence helper | Hybrid |
| 7 | Code Review (GitLab) | GitLab Duo review instructions, Copilot skill, prompt, interactive agent | AI-driven + deterministic checks |
| 8 | Security Checks | Security skill, prompt, read-only agent, scanner guidance | Hybrid |

This repository does **not** reimplement Copilot, GitLab Duo, Postman, draw.io, Atlassian, Dynatrace, Semgrep, or OWASP Dependency-Check. It packages reusable instructions and small helpers around those tools.

## Quick install from GitHub with npx

Developers do **not** need to clone this toolkit or install Python. They open their existing project in a terminal and run the command for the feature they need.

After you publish the CLI package as a GitHub Release asset (see [Publish the npx installer](#publish-the-npx-installer)), a developer can run:

```bash
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install drawio-diagram-generator
```

Other examples:

```bash
# List available features
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant list

# Install multiple features
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install log-analyzer code-review

# Preview an installation without writing files
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install drawio-diagram-generator --dry-run

# Install all features
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install --all

# Update an installed feature from the same release
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install drawio-diagram-generator --overwrite
```

Run the command **from the root of the target project**. The installer uses that current directory by default. You can also pass `--target "C:\work\my-project"`.

### What happens

1. `npx` downloads the small CLI package from the GitHub Release asset into the npm cache and runs it.
2. The CLI reads `manifest/features.json` from the configured GitHub repository using the GitHub Contents API.
3. It downloads only the files mapped to the selected feature and copies them into the current project.
4. Skills, agents, prompts, and helper files are installed into the paths defined in the manifest. For example, skills go to `.github/skills/`, agents to `.github/agents/`, and prompts to `.github/prompts/`.

The CLI package is deliberately small; it does not contain all feature content. The selected feature content is downloaded only when the developer asks to install that feature. The target project does not receive a clone of the toolkit repository.

### Requirements

- Node.js 18 or later (includes `fetch`) and npm/npx.
- Internet access to the GitHub Release download and GitHub API.
- For a public toolkit repository, no GitHub token is needed.
- For a private toolkit repository, the developer needs access to the repository and must provide a GitHub token with **Contents: read** permission as `GITHUB_TOKEN` or `GH_TOKEN`. Downloading the CLI tarball itself must also be authenticated; see `docs/DISTRIBUTION.md` for the private-repository caveat.

## Publish the npx installer

The package is a small CLI wrapper. Its `package.json` `files` list includes only `cli/**`, `README.md`, and `LICENSE` (plus npm-required package metadata); the actual skills, agents, prompts, and helpers are downloaded from the GitHub repository when a feature is installed.

Before the first release:

1. Push this repository to GitHub.
2. Edit `package.json` and replace `YOUR_GITHUB_ORG` in `repository.url` with the actual GitHub owner or organization. Keep `aiDevAssistant.ref` set to the release tag you plan to create, for example `v1.0.0`.
3. Set the package version to `1.0.0` (or your chosen version).
4. Run the tests and create the CLI tarball:

   ```bash
   npm test
   npm run package:cli
   ```

5. Create a GitHub Release named/tagged `v1.0.0` and upload `ai-dev-assistant-1.0.0.tgz` as a release asset.
6. Share the npx command above with developers, replacing `YOUR_GITHUB_ORG` if necessary.

For each toolkit update, increment the npm package version, update `aiDevAssistant.ref` to the new Git tag, package again, and attach the new `.tgz` file to the matching GitHub Release. Developers rerun the new command with `--overwrite` to update existing files; they should review the resulting Git diff.

## CLI commands

```text
ai-dev-assistant list
ai-dev-assistant install <feature-id> [feature-id ...]
ai-dev-assistant install --all
```

Options:

| Option | Purpose |
|---|---|
| `--repo OWNER/REPO` | Override the toolkit GitHub repository |
| `--ref REF` | Override the branch, tag, or commit (default comes from package configuration) |
| `--target PATH` | Install into a different existing project directory (default: current directory) |
| `--all` | Install all features |
| `--dry-run` | Preview files without writing them |
| `--overwrite` | Replace files that already exist |

For a private repository, set the token in the current shell before running the command. PowerShell example:

```powershell
$env:GITHUB_TOKEN = "YOUR_READ_ONLY_GITHUB_TOKEN"
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install drawio-diagram-generator
```

Do not put tokens in commands that may be saved in shell history, committed files, or shared documentation. Use your organization's approved token-management process.

## Existing local installers

The repository still includes local installers for developers who have downloaded or cloned the toolkit source:

Windows PowerShell (no Python required):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -List
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Target "C:\\work\\my-cap-project" -Features logging-advisor,code-review
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Target "C:\\work\\my-cap-project" -All
```

macOS / Linux or systems with Python:

```bash
python3 scripts/install.py --list
python3 scripts/install.py --target ../my-java-project --features logging-advisor code-review
python3 scripts/install.py --target ../my-cap-project --all
```

Both local installers use the same manifest and skip existing files by default.

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

## Reusing it across projects

Keep this repository as the **single source of truth**. Developers install selected files into each application repository. Review and commit the installed files like normal project customizations. The toolkit installer does not overwrite existing files unless `--overwrite` is requested.

The installer does not configure every external integration automatically. MCP servers, credentials, GitLab Duo licensing, external scanners, and project-specific rules still require separate setup and approval.

## Optional MCP integrations

MCP is only needed when an agent must call an external tool. It is not required for ordinary code analysis or for the included local scripts.

Examples:
- draw.io hosted MCP: `https://mcp.draw.io/mcp`
- Atlassian Rovo MCP: `https://mcp.atlassian.com/v2/mcp`

Configuration examples are in `integrations/mcp/`. Review your organization's security and admin policies before enabling a server. The examples are not automatically added to `.vscode/mcp.json`, because an existing MCP configuration must not be overwritten blindly.

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
├── cli/                     # Small npx installer package
├── docs/
├── integrations/
│   ├── gitlab/
│   └── mcp/
├── scripts/                 # Local Python and PowerShell installers
├── tests/
├── manifest/features.json
└── package.json
```

See `docs/GETTING_STARTED.md`, `docs/DISTRIBUTION.md`, `docs/FEATURES.md`, `docs/IMPLEMENTATION-PLAN.md`, and `docs/VS-CODE-FAQ.md` for details.
