# Distribution to project repositories

## Recommended model

Use this repository as the canonical source. Developers install only the selected feature files into each application repository. The npm CLI is a small distribution tool; feature contents remain in this repository and are retrieved from GitHub on demand.

## Install directly from a GitHub Release with npx

The developer does not clone the toolkit repository or download an installer file manually. They open a terminal at the root of the target project and run a command like:

```bash
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install drawio-diagram-generator
```

Other commands:

```bash
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant list
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install logging-advisor code-review
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install --all --dry-run
```

The CLI reads the repository URL and default feature ref from its package metadata. It calls the GitHub Contents API for `manifest/features.json`, then downloads only the source files mapped to the requested feature. It copies those files to the working directory (or `--target` path). The package tarball itself contains only the CLI, package metadata, README, and license, as restricted by the `files` field in `package.json`.

Requirements: Node.js 18+ and npm/npx. No Python or manual Git clone is required for the developer. The GitHub repository hosting the feature source and the GitHub Release asset must be accessible.

## Build and publish the CLI package

Before publishing:

1. Set `repository.url` in the root `package.json` to the real GitHub repository URL.
2. Set `aiDevAssistant.ref` to the source tag/branch that the CLI should install from (recommended: a release tag such as `v1.0.0`).
3. Set the npm package `version` to the same release version without the leading `v` (for example `1.0.0`).
4. Run tests and package the small CLI tarball:

   ```bash
   npm test
   npm run package:cli
   ```

5. Create a GitHub Release tagged `v1.0.0` and upload `ai-dev-assistant-1.0.0.tgz` as a release asset.
6. Share the npx command with the team.

The `files` allowlist in `package.json` intentionally excludes `.github/`, `.gitlab/`, `manifest/`, helper scripts, docs, and tests from the npx package. Feature files are fetched only after the developer selects a feature.

Repeat the process for each version. Increment `version`, update `aiDevAssistant.ref`, create the matching Git tag, package the CLI, and upload it to the matching release. Developers use the new release URL to get the new CLI and feature snapshot.

## CLI options

```text
ai-dev-assistant list
ai-dev-assistant install <feature-id> [feature-id ...]
ai-dev-assistant install --all
```

Options:

- `--repo OWNER/REPO`: override the GitHub repository from package metadata.
- `--ref REF`: override the branch, tag, or commit.
- `--target PATH`: install into another existing folder; default is the current directory.
- `--overwrite`: replace matching files. Without it, existing files are skipped.
- `--dry-run`: show planned copies without writing files.

## Private GitHub repositories

For feature-file downloads, set `GITHUB_TOKEN` or `GH_TOKEN` to a fine-grained token with read-only **Contents** permission. For PowerShell:

```powershell
$env:GITHUB_TOKEN = "YOUR_READ_ONLY_GITHUB_TOKEN"
npx --yes --package=https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant/releases/download/v1.0.0/ai-dev-assistant-1.0.0.tgz ai-dev-assistant install drawio-diagram-generator
```

This token handles the GitHub Contents API calls performed by the CLI. A private GitHub Release asset also needs to be downloaded with authentication; a plain unauthenticated release URL will not work. For a fully private toolkit, use an authenticated package-delivery method approved by your organization (for example, GitHub Packages or an internal npm registry) for the CLI tarball as well.

Do not embed tokens in package URLs, source files, shell commands stored in scripts, or committed `.npmrc` files. Use approved credential management.

## Existing local installers

The Python and PowerShell installers remain available when a developer has the toolkit source locally:

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -List
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Target "C:\src\my-cap-project" -Features logging-advisor,code-review
```

macOS/Linux:

```bash
python3 scripts/install.py --list
python3 scripts/install.py --target ../my-java-project --features logging-advisor code-review
```

## Updating an installed feature

Run the npx command from the target project again with `--overwrite`, using the new release URL. Review the Git diff and keep project-specific edits. The installer does not delete old files that are no longer present in a feature.

## Avoiding conflicts

- Existing files are skipped unless `--overwrite` is provided.
- If `.gitlab/duo/mr-review-instructions.yaml` already exists, merge the toolkit's review groups manually or overwrite only after backing up and reviewing the existing file.
- The installer does not modify an existing `.vscode/mcp.json`; MCP configuration must be merged deliberately.
- Keep project-specific instructions and secrets out of the central toolkit.
